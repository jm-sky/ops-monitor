# FEATURE-027: Wizualizacja podziału wag (worn vs base vs consumable)

**Status:** ✅ Completed | **Priority:** High | **Complexity:** Medium | **Version:** v2.29.0
**Category:** 📊 Wizualizacje / ⚖️ Kontrola wagi
**Related Features:** [FEATURE-019](./FEATURE-019-extended-charts.md) - Extended Charts

---

## 📋 Overview

Dodanie wizualizacji podziału wag kontenera na trzy kategorie:
- **Base weight** - podstawowa waga (wszystkie przedmioty, które nie są worn ani consumable)
- **Worn weight** - waga przedmiotów noszonych na sobie (wearable = true)
- **Consumable weight** - waga przedmiotów zużywalnych (consumable = true)

Inspiracja: LighterPack pokazuje podział wag, co pomaga użytkownikom zrozumieć, ile faktycznie waży plecak vs ile waży to, co noszą na sobie.

---

## 🎯 Goals

1. **Obliczanie wag per kategoria** - funkcja do obliczania wag base/worn/consumable
2. **Wizualizacja wykresu** - wykres kołowy lub słupkowy pokazujący podział wag
3. **Wyświetlanie w statystykach** - dodanie sekcji z podziałem wag w Container Details
4. **Legenda i tooltips** - wyjaśnienie co oznacza każda kategoria

---

## 📐 Design

### Lokalizacja

**Proponowane miejsca:**
1. **Sekcja statystyk kontenera** (`ContainerDetailPage.vue`) - nowa sekcja "Podział wag"
2. **Rozszerzenie istniejącego wykresu** (`CategoryPieChart.vue`) - nowy tryb "weight-breakdown"
3. **Osobny komponent** (`WeightBreakdownChart.vue`) - dedykowany komponent do podziału wag

**Rekomendacja:** Osobny komponent `WeightBreakdownChart.vue` + sekcja w statystykach kontenera

### Wizualizacja

**Opcja 1: Wykres kołowy (donut chart)**
- Podobny do istniejącego `CategoryPieChart.vue`
- 3 segmenty: Base (szary), Worn (niebieski), Consumable (zielony)
- Procentowy udział każdej kategorii
- Całkowita waga w środku

**Opcja 2: Wykres słupkowy (bar chart)**
- 3 słupki obok siebie
- Wysokość = waga w gramach/kg
- Kolorowe słupki z legendą

**Opcja 3: Karty z wartościami**
- 3 karty obok siebie
- Każda karta pokazuje: kategorię, wagę, procent
- Wizualne porównanie

**Rekomendacja:** Opcja 1 (wykres kołowy) - spójny z istniejącymi wykresami

### Kolory

- **Base weight:** Szary (`gray-500` / `muted`)
- **Worn weight:** Niebieski (`blue-500`)
- **Consumable weight:** Zielony (`green-500`)

---

## 🏗️ Implementation

### 1. Funkcje obliczeniowe

**Plik:** `src/modules/gear/utils/containerCalculations.ts`

```typescript
export interface WeightBreakdown {
  base: number      // Base weight in grams
  worn: number      // Worn weight in grams
  consumable: number // Consumable weight in grams
  total: number     // Total weight in grams
}

/**
 * Calculate weight breakdown for a container
 * @param container - Container to calculate breakdown for
 * @param allContainers - All containers (for nested container calculations)
 * @returns Weight breakdown with base, worn, consumable weights
 */
export function calculateWeightBreakdown(
  container: IGearContainer,
  allContainers: IGearContainer[],
): WeightBreakdown {
  let baseWeight = 0
  let wornWeight = 0
  let consumableWeight = 0

  // Add container's own weight to base (if not worn/consumable)
  if (isSet(container.weight) && isSet(container.weightUnit)) {
    const containerWeight = convertToGrams(container.weight, container.weightUnit)
    baseWeight += containerWeight
  }

  // Process items
  for (const item of container.items) {
    const itemWeight = convertToGrams(item.weight, item.weightUnit ?? 'g') * item.quantity

    // If item is a nested container, calculate its breakdown recursively
    if (item.containerId) {
      const nestedContainer = allContainers.find(c => c.id === item.containerId)
      if (nestedContainer) {
        const nestedBreakdown = calculateWeightBreakdown(nestedContainer, allContainers)
        const multiplier = item.quantity
        
        baseWeight += nestedBreakdown.base * multiplier
        wornWeight += nestedBreakdown.worn * multiplier
        consumableWeight += nestedBreakdown.consumable * multiplier
      }
    } else {
      // Regular item - categorize by wearable/consumable flags
      if (item.wearable) {
        wornWeight += itemWeight
      } else if (item.consumable) {
        consumableWeight += itemWeight
      } else {
        baseWeight += itemWeight
      }
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
```

### 2. Komponent wykresu

**Plik:** `src/modules/gear/components/WeightBreakdownChart.vue`

```vue
<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart'
import type { IGearContainer } from '../types/gear.types'
import { useGear } from '../composables/useGear'
import { useGearSettings } from '../composables/useGearSettings'
import { calculateWeightBreakdown } from '../utils/containerCalculations'
import { formatWeight } from '../utils/formatWeight'

const props = defineProps<{
  container: IGearContainer
  includeNested?: boolean
}>()

const { t } = useI18n()
const { containers } = useGear()
const { preferredWeightUnit } = useGearSettings()

const breakdown = computed(() => {
  return calculateWeightBreakdown(props.container, containers.value)
})

const chartData = computed(() => {
  const { base, worn, consumable, total } = breakdown.value
  
  return [
    {
      category: 'base',
      label: t('gear.weightBreakdown.base'),
      value: base,
      percentage: total > 0 ? (base / total) * 100 : 0,
      color: 'hsl(var(--muted))',
    },
    {
      category: 'worn',
      label: t('gear.weightBreakdown.worn'),
      value: worn,
      percentage: total > 0 ? (worn / total) * 100 : 0,
      color: 'hsl(var(--blue))',
    },
    {
      category: 'consumable',
      label: t('gear.weightBreakdown.consumable'),
      value: consumable,
      percentage: total > 0 ? (consumable / total) * 100 : 0,
      color: 'hsl(var(--green))',
    },
  ].filter(item => item.value > 0) // Only show categories with weight
})

const formattedTotal = computed(() => {
  return formatWeight(breakdown.value.total, preferredWeightUnit.value)
})
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>{{ t('gear.weightBreakdown.title') }}</CardTitle>
      <CardDescription>
        {{ t('gear.weightBreakdown.description') }}
      </CardDescription>
    </CardHeader>
    <CardContent>
      <!-- Chart implementation here -->
      <!-- Similar to CategoryPieChart.vue -->
    </CardContent>
  </Card>
</template>
```

### 3. Sekcja w Container Details

**Plik:** `src/modules/gear/pages/ContainerDetailPage.vue`

Dodaj sekcję z wykresem podziału wag w sekcji statystyk kontenera.

### 4. Tłumaczenia

**Plik:** `src/modules/gear/i18n/index.ts`

```typescript
weightBreakdown: {
  title: 'Weight Breakdown',
  description: 'Distribution of weight by category',
  base: 'Base Weight',
  worn: 'Worn Weight',
  consumable: 'Consumable Weight',
  baseDescription: 'Items carried in pack',
  wornDescription: 'Items worn on person',
  consumableDescription: 'Items that are consumed/used up',
}
```

---

## 📊 Edge Cases

1. **Przedmioty z oboma flagami** (wearable + consumable)
   - **Decyzja:** Priorytet: consumable > worn > base
   - Jeśli przedmiot ma obie flagi, traktuj jako consumable

2. **Puste kategorie**
   - Jeśli brak przedmiotów w kategorii, nie pokazuj segmentu na wykresie

3. **Zagnieżdżone kontenery**
   - Rekurencyjne obliczanie breakdown dla zagnieżdżonych kontenerów
   - Mnożenie przez quantity przedmiotu-kontenera

4. **Kontener bez przedmiotów**
   - Pokazuj tylko wagę samego kontenera (base)

---

## ✅ Acceptance Criteria

1. ✅ Funkcja `calculateWeightBreakdown()` oblicza poprawne wartości
2. ✅ Wykres pokazuje 3 kategorie (base, worn, consumable)
3. ✅ Wykres jest widoczny w sekcji statystyk kontenera
4. ✅ Tooltips pokazują wagę i procent dla każdej kategorii
5. ✅ Legenda wyjaśnia co oznacza każda kategoria
6. ✅ Obsługa zagnieżdżonych kontenerów (rekurencyjne obliczanie)
7. ✅ Obsługa przedmiotów z oboma flagami (priorytet consumable)
8. ✅ Formatowanie wag zgodne z preferowaną jednostką użytkownika
9. ✅ Tłumaczenia PL/EN
10. ✅ Responsywny design (mobile-friendly)

---

## 🔗 Related

- [FEATURE-019](./FEATURE-019-extended-charts.md) - Extended Charts (wykresy kategorii, cen, priorytetów)
- [FEATURE-003](./FEATURE-003-container-colors.md) - Container Colors
- [ROADMAP_OFFLINE.md](../ROADMAP_OFFLINE.md) - Kontrola wagi

---

## 📝 Notes

- Inspiracja: LighterPack pokazuje podział wag (base/worn/consumable)
- Możliwość rozszerzenia: dodanie wykresu słupkowego jako alternatywy
- Możliwość rozszerzenia: eksport breakdown do markdown/CSV
- Możliwość rozszerzenia: porównanie breakdown między kontenerami

