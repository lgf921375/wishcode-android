import {test} from 'node:test';
import assert from 'node:assert/strict';
import {requestBody,translate,generate,ENDPOINTS} from '../plugins/dsh-wishcode-glm/lib/protocol.js';
const options = {model:'glm-5.3',messages:[{role:'user',content:[{type:'text',text:'写网页'}]}]};
const collect = async iterator => {const out=[]; for await (const x of iterator) out.push(x); return out;};
function stream(packets, done = true) {
  const text=packets.map(x => 'data: '+JSON.stringify(x)+'\r\n\r\n').join('')+(done?'data: [DONE]\r\n\r\n':'');
  const bytes=new TextEncoder().encode(text);
  return new ReadableStream({start(c){for(let i=0;i<bytes.length;i+=3)c.enqueue(bytes.slice(i,i+3));c.close();}});
}
const chunk = (delta, finish_reason=null) => ({choices:[{delta,finish_reason}]});
test('official routes remain separate and forced thinking is serialized',()=>{
 assert.notEqual(ENDPOINTS.api,ENDPOINTS.plan);
 assert.match(ENDPOINTS.plan,/\/coding\/paas\/v4\/chat\/completions$/);
 for(const effort of ['low','high','max']) assert.equal(requestBody({...options,reasoningEffort:effort}).reasoning_effort,effort);
 assert.equal(requestBody(options).thinking.type,'enabled');
 assert.throws(()=>requestBody({...options,reasoningEffort:'off'}),/GLM_EFFORT/);
 assert.throws(()=>requestBody({...options,messages:[{role:'user',content:[{type:'image'}]}]}),/GLM_TEXT_ONLY/);
});
test('UTF-8 reasoning, text, interleaved tool fragments and cached usage assemble',async()=>{
 const result=await collect(translate(stream([
  chunk({reasoning_content:'先思考'}),chunk({content:'开始'}),
  chunk({tool_calls:[{index:0,id:'call1',function:{name:'bash',arguments:'{"cmd":'}},{index:1,id:'call2',function:{name:'read',arguments:'{"path":'}}]}),
  chunk({tool_calls:[{index:1,function:{arguments:'"a"}'}},{index:0,function:{arguments:'"pwd"}'}}]},'tool_calls'),
  {choices:[],usage:{prompt_tokens:100,completion_tokens:10,prompt_tokens_details:{cached_tokens:40}}}
 ])));
 const blocks=result.filter(x=>x.type==='block-end').map(x=>x.block);
 assert.deepEqual(blocks,[{type:'reasoning',text:'先思考'},{type:'text',text:'开始'},{type:'tool-call',id:'call1',name:'bash',arguments:'{"cmd":"pwd"}'},{type:'tool-call',id:'call2',name:'read',arguments:'{"path":"a"}'}]);
 assert.deepEqual(result.at(-2).usage,{inputTokens:60,outputTokens:10,cacheReadTokens:40,totalTokens:110});
 assert.equal(result.at(-1).reason.kind,'tool-calls');
 const body=requestBody({...options,messages:[...options.messages,{role:'assistant',content:blocks},{role:'tool',source:{callId:'call1'},content:[{type:'text',text:'/root'}]}]});
 assert.equal(body.messages[1].reasoning_content,'先思考'); assert.equal(body.messages[1].tool_calls[0].id,'call1'); assert.equal(body.messages[2].tool_call_id,'call1');
});
test('truncation, malformed tool JSON and provider errors never finish successfully',async()=>{
 await assert.rejects(collect(translate(stream([chunk({content:'half'})],false))),/INCOMPLETE_STREAM/);
 await assert.rejects(collect(translate(stream([chunk({tool_calls:[{index:0,id:'x',function:{name:'bash',arguments:'{'}}]},'tool_calls')]))));
 await assert.rejects(collect(translate(stream([{error:{message:'secret'}}]))),/GLM_PROVIDER_ERROR/);
});
test('single POST, no redirect or billing fallback; HTTP body not exposed',async()=>{
 let calls=0;
 await assert.rejects(collect(generate(options,'plan','test-key',{},async(url,init)=>{
  calls++;assert.equal(url,ENDPOINTS.plan);assert.equal(init.redirect,'error');assert.equal(init.headers.Authorization,'Bearer test-key');
  return new Response('private response test-key',{status:429});
 })),/^Error: GLM_HTTP_429$/);
 assert.equal(calls,1);
 await assert.rejects(collect(generate(options,'unknown','test-key',{},()=>{throw new Error('must not call');})),/GLM_CHANNEL/);
});
test('caller abort reaches transport and successful streams finish',async()=>{
 const control=new AbortController(); control.abort();
 await assert.rejects(collect(generate({...options,signal:control.signal},'api','test-key',{},async(url,init)=>{init.signal.throwIfAborted();})),{name:'AbortError'});
 const result=await collect(generate(options,'api','test-key',{},async()=>new Response(stream([chunk({content:'OK'},'stop')]))));
 assert.equal(result.at(-1).reason.kind,'stop');
});
