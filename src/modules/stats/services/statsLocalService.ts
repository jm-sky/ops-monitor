import { useGearStore } from '@/modules/gear/store/useGearStore'

/**
 * Stats Local Service
 * Calculates statistics from localStorage data
 */
class StatsLocalService {
  /**
   * Get current month start date
   */
  private getCurrentMonthStart(): Date {
    const now = new Date()
    return new Date(now.getFullYear(), now.getMonth(), 1)
  }

  /**
   * Check if date is within current month
   */
  private isThisMonth(dateString: string): boolean {
    const date = new Date(dateString)
    const monthStart = this.getCurrentMonthStart()
    return date >= monthStart
  }

  /**
   * Get user statistics
   * Note: Users are not stored locally, so this always returns 0
   */
  async getUserStats(): Promise<{ total: number; newThisMonth: number }> {
    return { total: 0, newThisMonth: 0 }
  }

  /**
   * Get container statistics from localStorage
   */
  async getContainerStats(): Promise<{ total: number; newThisMonth: number }> {
    const gearStore = useGearStore()
    const containers = gearStore.getAllContainers

    const total = containers.length
    const newThisMonth = containers.filter(c => this.isThisMonth(c.createdAt)).length

    return { total, newThisMonth }
  }

  /**
   * Get item statistics from localStorage
   */
  async getItemStats(): Promise<{ total: number; newThisMonth: number }> {
    const gearStore = useGearStore()
    const containers = gearStore.getAllContainers
    const allItems = containers.flatMap(c => c.items)

    const total = allItems.length
    const newThisMonth = allItems.filter(item => this.isThisMonth(item.createdAt)).length

    return { total, newThisMonth }
  }

  /**
   * Get all statistics
   */
  async getAllStats(): Promise<{
    users: { total: number; newThisMonth: number }
    containers: { total: number; newThisMonth: number }
    items: { total: number; newThisMonth: number }
  }> {
    const [users, containers, items] = await Promise.all([
      this.getUserStats(),
      this.getContainerStats(),
      this.getItemStats(),
    ])

    return { users, containers, items }
  }
}

export const statsLocalService = new StatsLocalService()
