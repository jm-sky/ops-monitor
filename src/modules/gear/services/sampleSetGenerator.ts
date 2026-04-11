import type {
  TGearItemCategory,
  TGearItemPriority,
  TGearItemQuality,
  TGearItemStatus,
  TGearWeightUnit,
} from '../types/gear.types'
import { validateContainerDto, validateItemDto } from '../utils/validation'
import {
  bugOutBagFirePouchItems,
  bugOutBagItems,
  edcItems,
  firePouchItems,
  type IExampleSetItem,
} from './exampleSets'
import { gearContainerService } from './gearContainerService'
import { gearItemService } from './gearItemService'
import type { TUUID } from '@/shared/types/base.type'

export type SampleSetVariant = 'firePouch' | 'bugOutBag' | 'edc' | 'budgetEdc' | 'mediumEdc'

interface ISampleSetItem {
  name: string
  catalogueItemId?: string
  category: TGearItemCategory
  weight: number
  weightUnit: TGearWeightUnit
  quantity?: number
  priority?: TGearItemPriority
  status?: TGearItemStatus
  brand?: string
  notes?: string
  color?: string
  price?: number
  currency?: string
  url?: string
  quality?: TGearItemQuality
  consumable?: boolean
}

interface ISampleSetContainer {
  name: string
  type: 'backpack' | 'bag' | 'pouch' | 'box' | 'cabinet' | 'vehicle' | 'shelf' | 'drawer' | 'case' | 'trunk' | 'other'
  description?: string
  items: ISampleSetItem[]
  nestedContainers?: ISampleSetContainer[]
}

/**
 * Generates a sample gear set with containers and items
 * @param t - Translation function from vue-i18n
 * @param variant - Variant of the sample set to generate
 * @returns Array of created container IDs
 */
export async function generateSampleSet(
  t: (key: string) => string,
  variant: SampleSetVariant = 'bugOutBag'
): Promise<TUUID[]> {
  const setDefinition = getSampleSetDefinition(t, variant)
  const containerIds: TUUID[] = []

  // M6 FIX: Validate container data before service call
  const mainContainerDto = validateContainerDto({
    name: setDefinition.name,
    type: setDefinition.type,
    description: setDefinition.description,
  })

  // Create main container
  const mainContainer = await gearContainerService().createContainer(mainContainerDto)
  containerIds.push(mainContainer.id)

  // Recursively create containers and items
  await createContainerWithItems(mainContainer.id, setDefinition)

  return containerIds
}

async function createContainerWithItems(
  containerId: TUUID,
  containerDef: ISampleSetContainer
): Promise<void> {
  // Create nested containers first
  const nestedContainerIds: Map<string, TUUID> = new Map()
  if (containerDef.nestedContainers) {
    for (const nestedDef of containerDef.nestedContainers) {
      // M6 FIX: Validate nested container data before service call
      const nestedContainerDto = validateContainerDto({
        name: nestedDef.name,
        type: nestedDef.type,
        description: nestedDef.description,
      })

      const nestedContainer = await gearContainerService().createContainer(nestedContainerDto)
      nestedContainerIds.set(nestedDef.name, nestedContainer.id)
      // Recursively create items in nested container
      await createContainerWithItems(nestedContainer.id, nestedDef)
    }
  }

  // Create items in this container
  for (const item of containerDef.items) {
    // Check if this item represents a nested container
    const nestedContainerId = nestedContainerIds.get(item.name)

    // M6 FIX: Validate item data before service call
    const itemDto = validateItemDto({
      name: item.name,
      catalogueItemId: item.catalogueItemId || undefined,
      category: item.category,
      weight: item.weight,
      weightUnit: item.weightUnit,
      quantity: item.quantity ?? 1,
      priority: item.priority ?? 'medium',
      status: item.status ?? 'owned',
      brand: item.brand,
      notes: item.notes,
      containerId: nestedContainerId || undefined,
      color: item.color,
      price: item.price,
      currency: item.currency,
      url: item.url,
      quality: item.quality,
      consumable: item.consumable,
    })

    await gearItemService().createItem(containerId, itemDto)
  }
}

/**
 * Helper function to translate with fallback
 * If translation returns the key (meaning translation not found), use fallback
 */
function translateWithFallback(
  t: (key: string, ...args: unknown[]) => string,
  key: string,
  fallback: string
): string {
  const translated = t(key)
  // If translation returns the key itself (or starts with the key pattern), it means translation was not found
  // vue-i18n may return the key with some prefix or modification when not found
  if (translated === key || translated.startsWith(key + '.') || translated.includes('[') && translated.includes(key)) {
    return fallback
  }
  return translated
}

/**
 * Converts example set items to sample set items with translated names and notes
 */
function translateItems(
  items: IExampleSetItem[],
  t: (key: string) => string
): ISampleSetItem[] {
  return items.map(item => {
    // Extract item key from full path (e.g., 'gear.sampleSet.items.lightMyFireFiresteel' -> 'lightMyFireFiresteel')
    const itemKey = item.nameKey.split('.').pop() || item.nameKey

    // Get translated name using new nested structure: gear.sampleSet.items.{itemKey}.name
    const nameKey = `${item.nameKey}.name`
    const fallbackName = itemKey
    const translatedName = translateWithFallback(t, nameKey, fallbackName)

    // Get translated notes using new nested structure: gear.sampleSet.items.{itemKey}.notes
    const notesKey = item.notesKey ? item.notesKey.replace('.notes', '.notes') : undefined
    const translatedNotes = notesKey
      ? translateWithFallback(t, notesKey, '')
      : undefined

    return {
      name: translatedName,
      catalogueItemId: item.catalogueItemId,
      category: item.category,
      weight: item.weight,
      weightUnit: item.weightUnit,
      quantity: item.quantity,
      priority: item.priority ?? 'medium',
      status: item.status ?? 'owned',
      brand: item.brand,
      notes: translatedNotes,
      color: item.color,
      price: item.price,
      currency: item.currency ?? 'USD',
      url: item.url,
      quality: item.quality,
      consumable: item.consumable,
    }
  })
}

function getSampleSetDefinition(
  t: (key: string) => string,
  variant: SampleSetVariant
): ISampleSetContainer {
  switch (variant) {
    case 'bugOutBag': {
      const firePouchName = translateWithFallback(
        t,
        'gear.sampleSet.variants.bugOutBag.firePouch',
        'Fire Pouch'
      )
      return {
        name: translateWithFallback(
          t,
          'gear.sampleSet.variants.bugOutBag.name',
          'Bug Out Bag'
        ),
        type: 'backpack',
        description: translateWithFallback(
          t,
          'gear.sampleSet.variants.bugOutBag.description',
          'Complete survival kit for emergency situations'
        ),
        nestedContainers: [
          {
            name: firePouchName,
            type: 'pouch',
            items: translateItems(bugOutBagFirePouchItems, t),
          },
        ],
        items: [
          ...translateItems(bugOutBagItems, t),
          {
            name: firePouchName,
            category: 'tools' as const,
            weight: 80,
            weightUnit: 'g' as const,
            quantity: 1,
            priority: 'high' as const,
            status: 'owned' as const,
          },
        ],
      }
    }

    case 'edc':
      return {
        name: translateWithFallback(
          t,
          'gear.sampleSet.variants.edc.name',
          'EDC (Every Day Carry)'
        ),
        type: 'bag',
        description: translateWithFallback(
          t,
          'gear.sampleSet.variants.edc.description',
          'Essential items for daily carry'
        ),
        items: translateItems(edcItems, t),
      }

    case 'firePouch':
      return {
        name: translateWithFallback(
          t,
          'gear.sampleSet.variants.firePouch.name',
          'Fire Pouch'
        ),
        type: 'pouch',
        description: translateWithFallback(
          t,
          'gear.sampleSet.variants.firePouch.description',
          'Minimalist fire starting kit'
        ),
        items: translateItems(firePouchItems, t),
      }

    default:
      throw new Error(`Unknown sample set variant: ${variant}`)
  }
}
