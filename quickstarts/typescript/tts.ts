/** Server-side Node example. Do not bundle this file into browser JavaScript. */
import { readFile, writeFile, access } from 'node:fs/promises';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ENDPOINT = 'https://tts.mayaresearch.ai/v1/tts';
const catalog: {models: Record<string, string[]>; languages: Record<string, string>} =
  JSON.parse(await readFile(new URL('../../docs/api-reference/catalog.json', import.meta.url), 'utf8'));

export function payload(text: string, model = 'Maya Calyx', voice = 'Aarav', language?: string) {
  if (typeof text !== 'string' || !text.trim() || [...text].length > 5000)
    throw new Error('Use 1-5000 characters of plain text');
  if (!catalog.models[model]?.includes(voice)) throw new Error('Invalid model/voice pair');
  if (language && !Object.hasOwn(catalog.languages, language)) throw new Error('Invalid language code');
  return { text, model, voice, ...(language ? { language } : {}) };
}

export function pcmRate(contentType: string): number {
  const parts = contentType.toLowerCase().split(';').map(x => x.trim());
  if (parts[0] !== 'audio/l16') throw new Error('Expected PCM audio/L16, not JSON, WAV or mu-law');
  const params = Object.fromEntries(parts.slice(1).map(x => x.split('=').map(v => v.trim().replaceAll('"', ''))));
  const rate = Number(params.rate);
  if (![8000, 16000, 24000].includes(rate) || Number(params.channels ?? 1) !== 1)
    throw new Error('Unsupported audio metadata');
  return rate;
}

export function wav(pcm: Buffer, rate: number): Buffer {
  if (!pcm.length || pcm.length % 2 || ![8000, 16000, 24000].includes(rate))
    throw new Error('Empty, truncated or unsupported PCM');
  const header = Buffer.alloc(44);
  header.write('RIFF', 0); header.writeUInt32LE(36 + pcm.length, 4);
  header.write('WAVEfmt ', 8); header.writeUInt32LE(16, 16);
  header.writeUInt16LE(1, 20); header.writeUInt16LE(1, 22);
  header.writeUInt32LE(rate, 24); header.writeUInt32LE(rate * 2, 28);
  header.writeUInt16LE(2, 32); header.writeUInt16LE(16, 34);
  header.write('data', 36); header.writeUInt32LE(pcm.length, 40);
  return Buffer.concat([header, pcm]);
}

export async function synthesize(body: ReturnType<typeof payload>, key: string,
  fetcher: typeof fetch = fetch, timeoutMs = 60000) {
  if (!key.trim() || /[\r\n]/.test(key)) throw new Error('Set MAYA_API_KEY in the environment');
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetcher(ENDPOINT, {
      method: 'POST', redirect: 'error', signal: controller.signal,
      headers: {'Authorization': `Bearer ${key}`, 'Content-Type': 'application/json',
        'User-Agent': 'maya-cookbook/0.1'},
      body: JSON.stringify(body),
    });
    if (response.status !== 200) {
      await response.body?.cancel();
      throw new Error(`Maya HTTP ${response.status}; see troubleshooting. Response is not audio.`);
    }
    const rate = pcmRate(response.headers.get('content-type') ?? '');
    if (!response.body) throw new Error('Missing audio body');
    const parts: Buffer[] = [];
    let total = 0;
    for await (const chunk of response.body) {
      total += chunk.length;
      if (total > 24000 * 2 * 120) throw new Error('Example audio budget exceeded');
      parts.push(Buffer.from(chunk));
    }
    return {audio: wav(Buffer.concat(parts), rate), rate, pcmBytes: total};
  } finally {
    controller.abort();
    clearTimeout(timer);
  }
}

async function main() {
  const { parseArgs } = await import('node:util');
  const { values } = parseArgs({ options: {
    text: {type:'string', default:'Hello! Your order will arrive tomorrow.'},
    model: {type:'string', default:process.env.MAYA_MODEL ?? 'Maya Calyx'},
    voice: {type:'string', default:process.env.MAYA_VOICE ?? 'Aarav'},
    language: {type:'string', default:process.env.MAYA_LANGUAGE || undefined},
    output: {type:'string', default:'output.wav'}, check: {type:'boolean', default:false},
  }});
  const body = payload(values.text!, values.model!, values.voice!, values.language);
  if (values.check) { console.log('Configuration valid. No API call made.'); return; }
  let exists = false;
  try { await access(values.output!); exists = true; } catch { /* checked again by wx */ }
  if (exists) throw new Error('Output exists. Choose a new --output path.');
  const result = await synthesize(body, process.env.MAYA_API_KEY ?? '');
  await writeFile(values.output!, result.audio, {flag:'wx'});
  console.log(JSON.stringify({output: values.output, sample_rate: result.rate, pcm_bytes: result.pcmBytes}));
}

if (process.argv[1] && fileURLToPath(import.meta.url) === fileURLToPath(pathToFileURL(process.argv[1]))) {
  main().catch((error: unknown) => {
    // Never dump fetch exceptions: some runtimes attach request headers to them.
    let message = error instanceof Error ? error.message : 'Synthesis failed';
    if (process.env.MAYA_API_KEY) message = message.replaceAll(process.env.MAYA_API_KEY, '[REDACTED]');
    console.error(`${message}. See docs/troubleshooting.md. No automatic retry.`);
    process.exitCode = 1;
  });
}
