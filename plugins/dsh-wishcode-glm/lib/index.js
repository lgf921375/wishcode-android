import {readFile} from 'node:fs/promises';
import {LlmAdapter, LlmError, attributionHeaders} from '@deepseek-ai/dsh-llm';
import {generate} from './protocol.js';
export const name = 'dsh-wishcode-glm';
const routes = {'wishcode-glm-api':'api','wishcode-glm-plan':'plan'};
const labels = {api:'智谱 GLM-5.3 · 普通 API',plan:'智谱 GLM-5.3 · Coding Plan 套餐'};
async function credentials() {
  try { return JSON.parse(await readFile('/root/.dsh/wishcode-glm.json','utf8')); }
  catch { return {}; } // Never include credential file content or parser errors in logs.
}
export class GlmAdapter extends LlmAdapter {
  providerInfo(provider) { return {id:provider,name:labels[routes[provider]]}; }
  async listModels(provider) { return [(await this.resolveModel(provider,'glm-5.3'))]; }
  async resolveModel(provider, model) {
    if (!routes[provider] || model !== 'glm-5.3') throw new LlmError('未知 GLM 模型','UNKNOWN_MODEL');
    return {provider,id:model,name:labels[routes[provider]],inputModalities:['text'],
      context:{contextWindow:1000000},defaultMaxTokens:16384,
      reasoning:{efforts:['low','high','max'].map(id => ({id,name:id})),defaultEffort:'max'}};
  }
  async *stream(options) {
    const channel = routes[options.provider];
    const config = await credentials();
    try { yield* generate(options,channel,config[channel],attributionHeaders()); }
    catch (error) {
      // Only our fixed diagnostic tokens may leave this adapter.
      const code = /^GLM_[A-Z0-9_]+$/.test(error.message) ? error.message : 'GLM_TRANSPORT';
      throw new LlmError(`${code}：请在许愿首页检查对应渠道的密钥、额度和网络。`,code);
    }
  }
}
export function apply(ctx) {
  ctx.inject(['llm'], child => { child.llm.registerAdapter(Object.keys(routes),new GlmAdapter()); });
}
