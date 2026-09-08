import test from 'node:test';
import assert from 'node:assert/strict';
import {payload, pcmRate, wav, synthesize} from './tts.ts';

for (const voice of ['Jackson','Riley','Vance','Christine','Christopher','Ananya','Arjun','Shailika','Gargi']) {
  test(`excluded speaker ${voice} fails before requests`, () => {
    assert.throws(() => payload('Hello','Maya Calyx',voice));
  });
}

for (const rate of [8000, 16000, 24000]) {
  test(`metadata and exact WAV bytes at ${rate}`, () => {
    assert.equal(pcmRate(`audio/L16; rate=${rate}; channels=1`), rate);
    const pcm = Buffer.from([1,2,254,255]); const output = wav(pcm, rate);
    assert.equal(output.toString('ascii', 0, 4), 'RIFF');
    assert.equal(output.readUInt32LE(24), rate);
    assert.equal(output.readUInt32LE(40), pcm.length);
    assert.deepEqual(output.subarray(44), pcm);
  });
}
for (const header of ['', 'application/json', 'audio/wav', 'audio/basic; rate=8000',
  'audio/L16', 'audio/L16; rate=44100', 'audio/L16; rate=24000; channels=2']) {
  test(`reject ${header}`, () => assert.throws(() => pcmRate(header)));
}
test('model and voice do not silently change', () => {
  assert.throws(() => payload('Hi','Maya Calyx','aarav'));
  assert.throws(() => payload('Hi','Unsupported Model','Aarav'));
  assert.throws(() => payload('Hi','Maya Calyx','Aarav','en-US'));
  assert.deepEqual(payload('Hi'), {text:'Hi',model:'Maya Calyx',voice:'Aarav'});
  assert.throws(() => payload(' ')); assert.throws(() => payload('x'.repeat(5001)));
  assert.equal(payload('नमस्ते hello').language, undefined);
});
for (const pcm of [Buffer.alloc(0), Buffer.from([0]), Buffer.from([0,1,2])]) {
  test(`reject incomplete PCM ${pcm.length}`, () => assert.throws(() => wav(pcm,24000)));
}
for (const status of [400,401,403,429,500,502]) {
  test(`HTTP ${status} is not saved or replayed`, async () => {
    let calls=0;
    const fake = (async () => {calls++; return new Response('{"error":"secret-canary"}', {status});}) as typeof fetch;
    await assert.rejects(synthesize(payload('Hi'),'test-key-not-live',fake), new RegExp(`HTTP ${status}`));
    assert.equal(calls,1);
  });
}
test('binary HTTP response is validated and preserved', async () => {
  const fake = (async (url, options) => {
    assert.equal(url,'https://tts.mayaresearch.ai/v1/tts');
    assert.equal(options?.redirect,'error');
    assert.ok(options?.signal);
    return new Response(new Uint8Array([1,2,3,4]), {headers:{'content-type':'audio/L16; rate=16000'}});
  }) as typeof fetch;
  const result = await synthesize(payload('Hi'),'test-key-not-live',fake);
  assert.deepEqual(result.audio.subarray(44),Buffer.from([1,2,3,4]));
});
test('JSON in a 200 is still not audio', async () => {
  const fake = (async () => new Response('{}',{headers:{'content-type':'application/json'}})) as typeof fetch;
  await assert.rejects(synthesize(payload('Hi'),'test-key-not-live',fake));
});
test('credential not configured means zero requests', async () => {
  let calls=0; const fake=(async()=>{calls++;return new Response();}) as typeof fetch;
  await assert.rejects(synthesize(payload('Hi'),'',fake)); assert.equal(calls,0);
});
test('slow request cancelled by total deadline', async () => {
  const fake=(async (_url,options)=> new Promise((_resolve,reject)=> {
    options?.signal?.addEventListener('abort',()=>reject(new Error('timeout')));
  })) as typeof fetch;
  await assert.rejects(synthesize(payload('Hi'),'test-key-not-live',fake,5));
});
