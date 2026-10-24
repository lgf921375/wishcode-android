// Official mainland endpoints only; never fall back between billing channels.
export const ENDPOINTS = Object.freeze({
  api: 'https://open.bigmodel.cn/api/paas/v4/chat/completions',
  plan: 'https://open.bigmodel.cn/api/coding/paas/v4/chat/completions',
});
export function requestBody(options) {
  if (options.model !== 'glm-5.3') throw new Error('GLM_MODEL');
  const effort = options.reasoningEffort ?? 'max';
  if (!['low', 'high', 'max'].includes(effort)) throw new Error('GLM_EFFORT');
  const messages = options.system ? [{role:'system', content:options.system}] : [];
  for (const m of options.messages) {
    if (!['system','user','assistant','tool'].includes(m.role)) throw new Error('GLM_ROLE');
    if (m.content.some(b => !['text','reasoning','tool-call'].includes(b.type)))
      throw new Error('GLM_TEXT_ONLY');
    const content = m.content.filter(b => b.type === 'text').map(b => b.text).join('\n');
    const out = {role:m.role, content};
    if (m.role === 'tool') {
      if (!m.source?.callId) throw new Error('GLM_TOOL_ID');
      out.tool_call_id = m.source.callId;
    }
    if (m.role === 'assistant') {
      out.reasoning_content = m.content.filter(b => b.type === 'reasoning').map(b => b.text).join('');
      const calls = m.content.filter(b => b.type === 'tool-call');
      if (calls.length) out.tool_calls = calls.map(b => ({id:b.id,type:'function',function:{name:b.name,arguments:b.arguments}}));
    }
    messages.push(out);
  }
  const maxTokens = options.maxTokens ?? 16384;
  if (!Number.isInteger(maxTokens) || maxTokens < 1 || maxTokens > 128000) throw new Error('GLM_MAX_TOKENS');
  return {model:'glm-5.3', messages, stream:true, tool_stream:true,
    thinking:{type:'enabled'}, reasoning_effort:effort, max_tokens:maxTokens,
    ...(options.tools?.length ? {tools:options.tools.map(t => ({type:'function',function:{name:t.name,description:t.description,parameters:t.parameters}}))} : {}),
    ...(options.stop?.length ? {stop:options.stop} : {})};
}

// SSE parser handles UTF-8 boundaries, CRLF, multiline data, usage-only frames and EOF.
export async function* events(body) {
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let buffer = '', data = [];
  try {
    while (true) {
      const {value, done} = await reader.read();
      buffer += done ? decoder.decode() : decoder.decode(value, {stream:true});
      let pos;
      while ((pos = buffer.indexOf('\n')) >= 0) {
        const line = buffer.slice(0,pos).replace(/\r$/, ''); buffer = buffer.slice(pos+1);
        if (!line) { if (data.length) { yield data.join('\n'); data=[]; } }
        else if (line.startsWith('data:')) data.push(line.slice(5).replace(/^ /,''));
      }
      if (buffer.length > 8 * 1024 * 1024 || data.join('').length > 8 * 1024 * 1024) throw new Error('GLM_FRAME_LIMIT');
      if (done) { if (buffer.startsWith('data:')) data.push(buffer.slice(5).trimStart()); if (data.length) yield data.join('\n'); return; }
    }
  } finally { await reader.cancel().catch(() => {}); reader.releaseLock(); }
}
export async function* translate(body) {
  const blocks = new Map(); let finish, usage;
  for await (const raw of events(body)) {
    if (raw === '[DONE]') break;
    const packet = JSON.parse(raw);
    if (packet.error) throw new Error('GLM_PROVIDER_ERROR');
    if (packet.usage) usage = packet.usage;
    const choice = packet.choices?.[0];
    if (!choice) continue;
    if (choice.finish_reason) finish = choice.finish_reason;
    const delta = choice.delta ?? {};
    for (const [field,type] of [['reasoning_content','reasoning'],['content','text']]) {
      if (!delta[field]) continue;
      let entry = blocks.get(field);
      if (!entry) { entry={index:blocks.size,block:{type,text:''}}; blocks.set(field,entry); yield {type:'block-start',index:entry.index,blockType:type}; }
      entry.block.text += delta[field];
      yield {type:type === 'text' ? 'text-delta':'reasoning-delta',index:entry.index,text:delta[field]};
    }
    for (const call of delta.tool_calls ?? []) {
      if (!Number.isInteger(call.index) || call.index < 0) throw new Error('GLM_TOOL_INDEX');
      const key = `tool:${call.index}`;
      let entry = blocks.get(key);
      if (!entry) { entry={index:blocks.size,block:{type:'tool-call',id:'',name:'',arguments:''}}; blocks.set(key,entry); yield {type:'block-start',index:entry.index,blockType:'tool-call'}; }
      if (call.id) entry.block.id = call.id;
      if (call.function?.name) entry.block.name += call.function.name;
      entry.block.arguments += call.function?.arguments ?? '';
      // Wait for a real provider id; never synthesize correlation ids.
      if (!entry.block.id) throw new Error('GLM_TOOL_ID');
      yield {type:'tool-call-delta',index:entry.index,id:entry.block.id,name:entry.block.name,argumentsDelta:call.function?.arguments ?? ''};
    }
  }
  if (!['stop','length','tool_calls'].includes(finish)) throw new Error('GLM_INCOMPLETE_STREAM');
  for (const entry of blocks.values()) {
    if (entry.block.type === 'tool-call') {
      if (!entry.block.id || !entry.block.name) throw new Error('GLM_INCOMPLETE_TOOL');
      JSON.parse(entry.block.arguments); // Malformed partial calls must never execute.
    }
    yield {type:'block-end',index:entry.index,block:entry.block};
  }
  if (usage && Number.isFinite(usage.prompt_tokens) && Number.isFinite(usage.completion_tokens)) {
    const cached = Math.min(usage.prompt_tokens, Math.max(0, usage.prompt_tokens_details?.cached_tokens ?? 0));
    yield {type:'usage',usage:{inputTokens:usage.prompt_tokens-cached,outputTokens:usage.completion_tokens,cacheReadTokens:cached,totalTokens:usage.prompt_tokens+usage.completion_tokens}};
  }
  yield {type:'finish',reason:{kind:finish === 'tool_calls' ? 'tool-calls' : finish === 'length' ? 'max-tokens' : 'stop'}};
}
export async function* generate(options, channel, apiKey, headers = {}, fetcher = fetch) {
  if (!Object.hasOwn(ENDPOINTS,channel)) throw new Error('GLM_CHANNEL');
  if (typeof apiKey !== 'string' || !apiKey.trim() || /\s/.test(apiKey)) throw new Error('GLM_KEY_REQUIRED');
  const body = requestBody(options);
  const control = new AbortController();
  const signal = options.signal ? AbortSignal.any([control.signal,options.signal]) : control.signal;
  const timer = setTimeout(() => control.abort(), 300000);
  try {
    // No retries, redirects, channel fallback, telemetry payloads or response-body logging.
    const response = await fetcher(ENDPOINTS[channel], {method:'POST',redirect:'error',signal,
      headers:{...headers,'Content-Type':'application/json',Accept:'text/event-stream',Authorization:`Bearer ${apiKey}`},body:JSON.stringify(body)});
    if (!response.ok) { await response.body?.cancel(); throw new Error(`GLM_HTTP_${response.status}`); }
    if (!response.body) throw new Error('GLM_EMPTY_RESPONSE');
    yield* translate(response.body);
  } finally { clearTimeout(timer); control.abort(); }
}
