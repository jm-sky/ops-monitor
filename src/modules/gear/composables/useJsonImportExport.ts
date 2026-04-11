import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { downloadBlob } from '@/shared/utils/downloadBlob'
import { useGear } from './useGear'

export const useJsonImportExport = () => {
    const { t } = useI18n()
    const { exportData, importData } = useGear()

    const genExportFilename = (): string => {
        return `gear-stack-export-${new Date().toISOString().split('T')[0]}.json`
    }

    const handleJsonExport = async () => {
        try {
          const json = await exportData()
          const blob = new Blob([json], { type: 'application/json' })
          const filename = genExportFilename()
          downloadBlob(blob, filename)
          toast.success(t('common.success'))
        } catch {
          toast.error(t('common.error'))
        }
      }
      
      const handleJsonImport = () => {
        // Use native input element for file selection
        const createInput = (): HTMLInputElement => {
            const input = document.createElement('input')
            input.type = 'file'
            input.accept = 'application/json'
            return input
        }

        const onReaderLoadHandler = async (event: ProgressEvent<FileReader>) => {
            try {
                const json = event.target?.result as string
                await importData(json)
                toast.success(t('common.success'))
                // Reload page to show imported data
                window.location.reload()
            } catch (error) {
                toast.error(t('common.error'))
                console.error('Import error:', error)
            }
        }

        const onChangeHandler = (e: Event) => {
            const file = (e.target as HTMLInputElement).files?.[0]
            if (!file) return
        
            const reader = new FileReader()
            reader.onload = (e) => onReaderLoadHandler(e)
            reader.readAsText(file)
        }

        const input = createInput()
        input.onchange = (e) => onChangeHandler(e)
        input.click()
      }

      return {
        handleJsonExport,
        handleJsonImport,
      }
}
