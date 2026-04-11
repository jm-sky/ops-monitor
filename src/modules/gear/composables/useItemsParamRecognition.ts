import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import type { IGearContainer, IGearItem } from '../types/gear.types'
import { recognizeParameters, recognizeParametersForItems } from '../utils/parameterRecognition'
import { useGear } from './useGear'
import type { ComputedRef } from 'vue'

export const useItemsParamRecognition = (
    container: ComputedRef<IGearContainer | undefined>,
    items: ComputedRef<IGearItem[]>
) => {
    const { t } = useI18n()
    const { updateItem } = useGear()

    const handleRecognizeParameters = async (item: IGearItem) => {
        try {
          const params = recognizeParameters(item.name)
      
          if (!params.brand && !params.color) {
            toast.info(t('gear.actions.noParametersFound'))
            return
          }
      
          const updateData: Partial<IGearItem> = {}
          if (params.brand && !item.brand) {
            updateData.brand = params.brand
          }
          if (params.color && !item.color) {
            updateData.color = params.color
          }
      
          if (Object.keys(updateData).length > 0) {
            await updateItem(item.id, updateData)
            toast.success(t('gear.actions.parametersRecognized'))
          } else {
            toast.info(t('gear.actions.noParametersFound'))
          }
        } catch (error) {
          toast.error(t('common.error'))
          console.error('Error recognizing parameters:', error)
        }
      }

    const handleRecognizeParametersAll = async () => {
        if (!container.value || !items.value || items.value.length === 0) return
      
        try {
          toast.loading(t('gear.actions.recognizing'))
      
          const paramsMap = recognizeParametersForItems(items.value)
          let updatedCount = 0
      
          for (const item of items.value) {
            const params = paramsMap.get(item.id)
            if (!params) continue
      
            const updateData: Partial<IGearItem> = {}
            if (params.brand && !item.brand) {
              updateData.brand = params.brand
            }
            if (params.color && !item.color) {
              updateData.color = params.color
            }
      
            if (Object.keys(updateData).length > 0) {
              await updateItem(item.id, updateData)
              updatedCount++
            }
          }
      
          toast.dismiss()
          if (updatedCount > 0) {
            toast.success(t('gear.actions.parametersRecognized', { count: updatedCount }))
          } else {
            toast.info(t('gear.actions.noParametersFound'))
          }
        } catch (error) {
          toast.dismiss()
          toast.error(t('common.error'))
          console.error('Error recognizing parameters:', error)
        }
      }

      return {
        handleRecognizeParameters,
        handleRecognizeParametersAll,
      }
}