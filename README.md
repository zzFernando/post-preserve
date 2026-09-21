# PostPreserve

Arquiva um post público do Instagram em um pacote verificável.

Uma URL entra; um ZIP sai contendo:

- o WACZ reproduzível, com os recursos capturados;
- uma screenshot PNG;
- metadados e relatório da captura;
- manifesto de checksums SHA-256;
- resultado da validação do pacote.

## Instalação

Requer [Pixi](https://pixi.sh). Não usa Docker, Colima ou máquina virtual.

```bash
pixi install
pixi run setup
pixi run doctor
```

O `setup` instala o Scoop e o Chromium uma única vez. Node 20 e Python 3.12 são
fixados pelo Pixi para tornar a execução reproduzível.

## Uso

```bash
pixi run postpreserve archive \
  "https://www.instagram.com/p/EXAMPLE/" \
  --output ./workspace/output
```

O resultado fica em `workspace/output/PP-IG-ANO-NÚMERO.zip`. Arquivos de trabalho
são temporários e apagados automaticamente; não ficam cópias duplicadas do WACZ.

Para validar ou inspecionar um arquivo:

```bash
pixi run postpreserve validate ./workspace/output/PP-IG-2026-000001.zip
pixi run postpreserve inspect ./post.wacz
```

O comando termina com código `0` para captura completa, `2` para parcial e `1`
para falha.

## Estrutura do ZIP

```text
data/web/post.wacz
data/representations/screenshot.png
metadata/metadata.json
metadata/source-metadata.json
metadata/capture-report.json
documentation/README.txt
manifest-sha256.txt
package-validation.json
```

## Desenvolvimento

```bash
pixi run lint
pixi run test
```

## Limites

- Apenas posts públicos do Instagram são suportados.
- Login, CAPTCHA, bloqueios e limites da plataforma não são contornados.
- A fidelidade depende do conteúdo que o Instagram entregar ao Chromium durante a captura.

PostPreserve não é afiliado à Meta ou ao Instagram. O uso deve respeitar direitos
autorais, privacidade, políticas institucionais e os termos da plataforma.

## Licença

Apache-2.0. O backend [Scoop](https://github.com/harvard-lil/scoop) é distribuído
sob licença MIT.
