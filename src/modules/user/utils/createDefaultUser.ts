import type { IUser } from '../types/user.types'

export const createDefaultUser = (): IUser => {
  const now = new Date().toISOString()
  return {
    id: crypto.randomUUID(),
    name: 'User',
    email: 'user@example.com',
    createdAt: now,
    updatedAt: now,
  }
}
