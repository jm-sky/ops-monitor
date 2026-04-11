import { useContainerCalculations } from './internal/useContainerCalculations'
import { useContainerImportExport } from './internal/useContainerImportExport'
import { useContainerOperations } from './internal/useContainerOperations'
import { useItemCatalog } from './internal/useItemCatalog'
import { useItemOperations } from './internal/useItemOperations'

/**
 * Main gear composable (Facade Pattern)
 *
 * This composable acts as a facade over focused internal composables.
 * It maintains backward compatibility while keeping the codebase organized.
 *
 * ⚠️ REFACTORED: This was previously a mega-composable with 24+ functions.
 * Now it composes 5 focused internal composables for better maintainability.
 *
 * Internal composables (in ./internal/):
 * - useContainerOperations - Container CRUD (7 functions)
 * - useItemOperations - Item CRUD (4 functions)
 * - useContainerCalculations - Calculations (8 functions)
 * - useContainerImportExport - Import/Export/Clone (3 functions)
 * - useItemCatalog - Catalog operations (2 functions)
 *
 * Usage remains the same:
 * ```ts
 * const { containers, createContainer, updateItem } = useGear()
 * ```
 */
export function useGear() {
  const containerOps = useContainerOperations()
  const itemOps = useItemOperations()
  const calculations = useContainerCalculations()
  const importExport = useContainerImportExport()
  const catalog = useItemCatalog()

  return {
    // State
    containers: containerOps.containers,

    // Container Operations (7)
    createContainer: containerOps.createContainer,
    updateContainer: containerOps.updateContainer,
    deleteContainer: containerOps.deleteContainer,
    deleteAllContainers: containerOps.deleteAllContainers,
    getContainerById: containerOps.getContainerById,
    getRootContainers: containerOps.getRootContainers,
    getNestedContainers: containerOps.getNestedContainers,

    // Item Operations (5)
    createItem: itemOps.createItem,
    updateItem: itemOps.updateItem,
    deleteItem: itemOps.deleteItem,
    getItemById: itemOps.getItemById,
    moveItem: itemOps.moveItem,

    // Calculations (7)
    calculateTotalWeight: calculations.calculateTotalWeight,
    calculateReadinessPercentage: calculations.calculateReadinessPercentage,
    calculateWeightLimitPercentage: calculations.calculateWeightLimitPercentage,
    isWeightLimitExceeded: calculations.isWeightLimitExceeded,
    getItemsByStatus: calculations.getItemsByStatus,
    getExpiredItems: calculations.getExpiredItems,
    getExpiringSoonItems: calculations.getExpiringSoonItems,

    // Import/Export/Clone (3)
    exportData: importExport.exportData,
    importData: importExport.importData,
    cloneContainer: importExport.cloneContainer,

    // Item Catalog (2)
    getAllItemsForCatalog: catalog.getAllItemsForCatalog,
    getItemWithContainer: catalog.getItemWithContainer,
  }
}

