import { useRef, useEffect, useState, useCallback } from 'react'

interface Props {
  value?: string
  onChange?: (value: string) => void
  language?: 'yaml' | 'json'
  height?: number
}

const YAML_KW = ['steps:', 'pipeline_', 'validate:', 'transform:', 'aggregate:', 'regras:',
  '- calcular:', '- validate:', '- transform:', '- aggregate:', 'group_by:', 'aggregations:',
  'sum(', 'avg(', 'calcular:', 'nome:', 'formula:', 'source:', 'output:', 'refresh:']
const STRING_RE = /"[^"]*"|'[^']*'/g
const COMMENT_RE = /#.*$/gm
const NUM_RE = /\b\d+(\.\d+)?\b/g

function highlight(text: string, lang: string): string {
  let html = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  html = html.replace(COMMENT_RE, (m) => `<span style="color:#6a9955">${m}</span>`)
  html = html.replace(STRING_RE, (m) => `<span style="color:#ce9178">${m}</span>`)
  const keywords = lang === 'yaml' ? YAML_KW : ['"colunas"', '"nome"', '"tipo"', '"obrigatorio"', '"mapeamento"']
  for (const kw of keywords) {
    html = html.replace(new RegExp(kw.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'),
      `<span style="color:#569cd6;font-weight:bold">${kw}</span>`)
  }
  html = html.replace(NUM_RE, (m) => `<span style="color:#b5cea8">${m}</span>`)
  if (lang === 'json') html = html.replace(/\b(true|false|null)\b/g, `<span style="color:#569cd6">$1</span>`)
  html = html.replace(/\b(\w+)(?=\s*:)/g, `<span style="color:#9cdcfe">$1</span>`)
  return html
}

export default function FormCodeEditor({ value, onChange, language = 'yaml', height = 300 }: Props) {
  const textRef = useRef<HTMLTextAreaElement>(null)
  const hlRef = useRef<HTMLDivElement>(null)
  const [lines, setLines] = useState(1)
  const text = value ?? ''

  useEffect(() => {
    setLines(text.split('\n').length || 1)
  }, [text])

  const handleChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange?.(e.target.value)
  }, [onChange])

  const syncScroll = useCallback(() => {
    if (textRef.current && hlRef.current) {
      hlRef.current.scrollTop = textRef.current.scrollTop
      hlRef.current.scrollLeft = textRef.current.scrollLeft
    }
  }, [])

  return (
    <div style={{
      position: 'relative', border: '1px solid #3c3c3c', borderRadius: 6,
      background: '#1e1e1e', overflow: 'hidden',
    }}>
      <div style={{ display: 'flex' }}>
        <div style={{
          width: 36, background: '#1e1e1e', color: '#858585', fontSize: 13,
          fontFamily: "'Consolas', 'Cascadia Code', monospace", lineHeight: '21px',
          padding: '10px 6px 10px 10px', textAlign: 'right', userSelect: 'none',
          borderRight: '1px solid #333',
        }}>
          {Array.from({ length: lines }, (_, i) => <div key={i}>{i + 1}</div>)}
        </div>
        <div style={{ position: 'relative', flex: 1, minHeight: height }}>
          <div ref={hlRef} style={{
            position: 'absolute', inset: 0, padding: '10px',
            fontSize: 13, fontFamily: "'Consolas', 'Cascadia Code', monospace",
            lineHeight: '21px', color: '#d4d4d4', whiteSpace: 'pre-wrap',
            wordBreak: 'break-word', overflow: 'hidden', pointerEvents: 'none',
          }} dangerouslySetInnerHTML={{ __html: highlight(text, language) + '\n' }} />
          <textarea ref={textRef}
            value={text}
            onChange={handleChange}
            onScroll={syncScroll}
            spellCheck={false}
            style={{
              position: 'absolute', inset: 0, padding: '10px',
              fontSize: 13, fontFamily: "'Consolas', 'Cascadia Code', monospace",
              lineHeight: '21px', color: 'transparent', caretColor: '#fff',
              background: 'transparent', border: 'none', outline: 'none',
              resize: 'vertical', minHeight: height, whiteSpace: 'pre-wrap',
              wordBreak: 'break-word', overflow: 'auto',
            }}
          />
        </div>
      </div>
    </div>
  )
}
