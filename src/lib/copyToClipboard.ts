export type CopyToClipboardResult = 'copied' | 'selected' | 'failed'

export type CopyToClipboardOptions = {
  selectElement?: HTMLElement
}

function legacyCopy(text: string): boolean {
  const textarea = document.createElement('textarea')
  textarea.value = text
  textarea.style.position = 'fixed'
  textarea.style.left = '-9999px'
  textarea.style.opacity = '0'
  document.body.appendChild(textarea)
  textarea.focus()
  textarea.select()

  try {
    return document.execCommand('copy')
  } catch {
    return false
  } finally {
    document.body.removeChild(textarea)
  }
}

function selectElementContents(element: HTMLElement): boolean {
  const selection = window.getSelection()
  if (!selection) return false

  selection.removeAllRanges()
  const range = document.createRange()
  range.selectNodeContents(element)
  selection.addRange(range)
  return selection.toString().length > 0
}

export async function copyToClipboard(
  text: string,
  options: CopyToClipboardOptions = {},
): Promise<CopyToClipboardResult> {
  if (!text) return 'failed'

  if (window.isSecureContext && navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(text)
      return 'copied'
    } catch {
      // Fall through to legacy copy.
    }
  }

  if (legacyCopy(text)) return 'copied'

  if (options.selectElement && selectElementContents(options.selectElement)) {
    return 'selected'
  }

  return 'failed'
}
