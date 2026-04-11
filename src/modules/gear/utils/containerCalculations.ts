import type { IGearContainer, IGearItem, TGearItemPriority } from '../types/gear.types'
import { getCurrency } from './currencyFormatter'
import { convertToGrams } from './formatWeight'
import { isSet } from './helpers'

/**
 * Calculate total weight of a container synchronously (for use in computed)
 * @param container - Container to calculate weight for
 * @param allContainers - All containers (for nested container calculations)
 * @returns Total weight in grams
 */
export function calculateTotalWeightSync(
  container: IGearContainer,
  allContainers: IGearContainer[],
): number {
  // Start with container's own weight (if set)
  let totalWeight = 0
  if (isSet(container.weight) && isSet(container.weightUnit)) {
    totalWeight = convertToGrams(container.weight, container.weightUnit)
  }

  // Add weight of direct items
  for (const item of container.items) {
    // If item is a nested container, calculate its total weight recursively
    if (item.containerId) {
      const nestedContainer = allContainers.find(c => c.id === item.containerId)
      if (nestedContainer) {
        const nestedContainerWeight = calculateTotalWeightSync(nestedContainer, allContainers)
        totalWeight += nestedContainerWeight * item.quantity
      }
    } else {
      // Regular item weight
      const weightInGrams = convertToGrams(item.weight, item.weightUnit ?? 'g')
      totalWeight += weightInGrams * item.quantity
    }
  }

  return totalWeight
}

/**
 * Calculate readiness percentage synchronously (for use in computed)
 * @param container - Container to calculate readiness for
 * @returns Readiness percentage (0-100)
 */
export function calculateReadinessPercentageSync(container: IGearContainer): number {
  if (!container || container.items.length === 0) {
    return 0
  }

  const ownedItems = container.items.filter(item => item.status === 'owned').length
  return Math.round((ownedItems / container.items.length) * 100)
}

/**
 * Calculate weight limit percentage synchronously (for use in computed)
 * @param container - Container to calculate weight limit for
 * @param allContainers - All containers (for nested container calculations)
 * @returns Weight limit percentage (0-100+) or null if no limit
 */
export function calculateWeightLimitPercentageSync(
  container: IGearContainer,
  allContainers: IGearContainer[],
): number | null {
  if (!container || !isSet(container.maxWeight)) {
    return null
  }

  const totalWeight = calculateTotalWeightSync(container, allContainers)
  const maxWeightInGrams = convertToGrams(container.maxWeight, container.maxWeightUnit ?? 'g')

  if (maxWeightInGrams === 0) {
    return 0
  }

  return Math.round((totalWeight / maxWeightInGrams) * 100)
}

/**
 * Calculate total price of a container synchronously (for use in computed)
 * Groups prices by currency and returns totals per currency
 * @param container - Container to calculate price for
 * @param allContainers - All containers (for nested container calculations)
 * @param defaultCurrency - Default currency to use when item/container has no currency
 * @returns Object with currency totals: { [currency: string]: number }
 */
export function calculateTotalPriceSync(
  container: IGearContainer,
  allContainers: IGearContainer[],
  defaultCurrency: string,
): Record<string, number> {
  const totals: Record<string, number> = {}

  // Helper to add price to totals
  const addPrice = (price: number | null | undefined, currency: string | null | undefined) => {
    if (price == null || price <= 0) return
    const curr = getCurrency(currency, defaultCurrency)
    totals[curr] = (totals[curr] || 0) + price
  }

  // Add container's own price (if set)
  addPrice(container.price, container.currency)

  // Add prices of direct items
  for (const item of container.items) {
    // If item is a nested container, calculate its total price recursively
    if (item.containerId) {
      const nestedContainer = allContainers.find(c => c.id === item.containerId)
      if (nestedContainer) {
        const nestedTotals = calculateTotalPriceSync(nestedContainer, allContainers, defaultCurrency)
        // Multiply by quantity and add to totals
        for (const [currency, amount] of Object.entries(nestedTotals)) {
          totals[currency] = (totals[currency] || 0) + amount * item.quantity
        }
      }
    } else {
      // Regular item price (multiply by quantity)
      if (item.price != null && item.price > 0) {
        const curr = getCurrency(item.currency, defaultCurrency)
        totals[curr] = (totals[curr] || 0) + item.price * item.quantity
      }
    }
  }

  return totals
}

/**
 * Calculate price distribution by category
 * @param items - Items to calculate price distribution for
 * @returns Array of category price data with totals and percentages
 */
export function calculatePriceByCategory(
  items: IGearItem[],
): Array<{ category: string; totalPrice: number; percentage: number }> {
  const categoryMap = new Map<string, number>()
  let totalPrice = 0

  items.forEach(item => {
    if (item.price != null && item.price > 0 && item.quantity > 0) {
      const itemTotal = item.price * item.quantity
      const category = item.category || 'other'
      const current = categoryMap.get(category) || 0
      categoryMap.set(category, current + itemTotal)
      totalPrice += itemTotal
    }
  })

  return Array.from(categoryMap.entries())
    .map(([category, price]) => ({
      category,
      totalPrice: price,
      percentage: totalPrice > 0 ? (price / totalPrice) * 100 : 0,
    }))
    .sort((a, b) => b.totalPrice - a.totalPrice)
}

/**
 * Calculate item distribution by priority
 * @param items - Items to calculate priority distribution for
 * @returns Array of priority data with counts and percentages
 */
export function calculateItemsByPriority(
  items: IGearItem[],
): Array<{ priority: TGearItemPriority; count: number; percentage: number }> {
  const priorityMap = new Map<TGearItemPriority, number>()

  items.forEach(item => {
    const priority = item.priority || 'medium'
    const current = priorityMap.get(priority) || 0
    priorityMap.set(priority, current + (item.quantity || 1))
  })

  const totalQuantity = Array.from(priorityMap.values()).reduce((a, b) => a + b, 0)

  const result = Array.from(priorityMap.entries())
    .map(([priority, count]) => ({
      priority,
      count,
      percentage: totalQuantity > 0 ? (count / totalQuantity) * 100 : 0,
    }))
    .sort((a, b) => {
      // Sort by priority order: critical, high, medium, low
      const order: Record<TGearItemPriority, number> = {
        critical: 0,
        high: 1,
        medium: 2,
        low: 3,
      }
      return order[a.priority] - order[b.priority]
    })

  return result
}

/**
 * Weight breakdown interface
 */
export interface WeightBreakdown {
  base: number      // Other items weight in grams (not worn or consumable)
  worn: number      // Worn weight in grams
  consumable: number // Consumable weight in grams
  total: number     // Total weight in grams
}

/**
 * Calculate weight breakdown for a container
 * Categorizes items by wearable/consumable flags
 * Priority: consumable > worn > other (if item has both flags, treat as consumable)
 * @param container - Container to calculate breakdown for
 * @param allContainers - All containers (for nested container calculations - not used for now)
 * @returns Weight breakdown with other, worn, consumable weights
 */
export function calculateWeightBreakdown(container: IGearContainer): WeightBreakdown {
  let baseWeight = 0
  let wornWeight = 0
  let consumableWeight = 0

  // Add container's own weight to other category (if set)
  if (isSet(container.weight) && isSet(container.weightUnit)) {
    const containerWeight = convertToGrams(container.weight, container.weightUnit)
    baseWeight += containerWeight
  }

  // Process direct items only (no nested containers for now)
  for (const item of container.items) {
    // Skip nested containers for now
    if (item.containerId) {
      continue
    }

    const itemWeight = convertToGrams(item.weight, item.weightUnit ?? 'g') * item.quantity

    // Categorize by wearable/consumable flags
    // Priority: consumable > worn > base
    if (item.consumable) {
      consumableWeight += itemWeight
    } else if (item.wearable) {
      wornWeight += itemWeight
    } else {
      baseWeight += itemWeight
    }
  }

  const total = baseWeight + wornWeight + consumableWeight

  return {
    base: baseWeight,
    worn: wornWeight,
    consumable: consumableWeight,
    total,
  }
}

