import fs from 'node:fs/promises'
import path from 'node:path'

import { Scoop } from '@harvard-lil/scoop'

const [url, output, summaryOutput, attachmentsDir, timeout, headless, proxyPort] = process.argv.slice(2)
const keepAlive = setInterval(() => {}, 1000)

try {
  const capture = await Scoop.capture(url, {
    captureTimeout: Number(timeout),
    headless: headless === 'true',
    screenshot: true,
    pdfSnapshot: false,
    domSnapshot: false,
    captureVideoAsAttachment: false,
    captureCertificatesAsAttachment: false,
    provenanceSummary: false,
    proxyHost: '127.0.0.1',
    proxyPort: Number(proxyPort),
    logLevel: process.env.POSTPRESERVE_DEBUG ? 'info' : 'warn'
  })
  if (!capture || capture.state === Scoop.states.FAILED) throw new Error('Capture failed')

  await fs.writeFile(output, Buffer.from(await capture.toWACZ()))
  await fs.writeFile(summaryOutput, JSON.stringify(await capture.summary(), null, 2))
  const attachments = await capture.extractGeneratedExchanges()
  for (const [filename, exchange] of Object.entries(attachments)) {
    await fs.writeFile(path.join(attachmentsDir, filename), exchange.response.body)
  }
} catch (error) {
  console.error(error.message)
  process.exitCode = 1
} finally {
  clearInterval(keepAlive)
}
