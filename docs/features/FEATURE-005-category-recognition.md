# FEATURE-005: Category Recognition

**Status:** ✅ Completed  
**Priority:** Medium  
**Category:** ⚡ Item Addition Improvements  
**Related:** ROADMAP.md - Usprawnienia dodawania przedmiotów

---

## 📋 Overview

Automatic category recognition for items and container type recognition for containers based on keywords in the name. This speeds up item creation by automatically detecting the appropriate category/type when the user types the name.

---

## 🎯 Goals

- Automatically detect item category from name using keyword matching
- Automatically detect container type from name using keyword matching
- Support both Polish and English keywords
- Only auto-detect when category/type is still at default value
- Improve UX by reducing manual selection

---

## 🔍 Current State

- Item forms exist with category selection
- Container forms exist with type selection
- Default values are set (category: 'other', type: 'other')

**What's missing:**
- Keyword dictionary for categories
- Keyword dictionary for container types
- Recognition logic
- Integration with forms

---

## 📝 Implementation Plan

### Step 1: Create Category Recognition Utility

**File:** `src/modules/gear/utils/categoryRecognition.ts`

- Dictionary of keywords for each category (PL and EN)
- Function to recognize category from name
- Case-insensitive matching

### Step 2: Create Container Type Recognition Utility

**File:** `src/modules/gear/utils/containerTypeRecognition.ts`

- Dictionary of keywords for each container type (PL and EN)
- Function to recognize container type from name
- Case-insensitive matching

### Step 3: Integrate with Item Form

**File:** `src/modules/gear/pages/ItemFormPage.vue`

- Add `@blur` handler on name field
- Auto-detect category when user leaves name field (blur event)
- Only update if category is still "other" (default)
- Only for new items, not when editing

**File:** `src/modules/gear/components/ItemFormFields.vue`

- Add `@blur` event on Input component
- Emit `nameBlur` event to parent

### Step 4: Integrate with Container Form

**File:** `src/modules/gear/pages/ContainerFormPage.vue`

- Add `@blur` handler on name field
- Auto-detect container type when user leaves name field (blur event)
- Only update if type is still "other" (default)
- Only for new containers, not when editing

**File:** `src/modules/gear/components/ContainerFormFields.vue`

- Add `@blur` event on Input component
- Emit `nameBlur` event to parent

---

## 📁 Files Created/Modified

**New Files:**
- `src/modules/gear/utils/categoryRecognition.ts` - Category recognition utility
- `src/modules/gear/utils/containerTypeRecognition.ts` - Container type recognition utility

**Files Modified:**
- `src/modules/gear/pages/ItemFormPage.vue` - Auto-detect category from name on blur
- `src/modules/gear/components/ItemFormFields.vue` - Add blur event handler
- `src/modules/gear/pages/ContainerFormPage.vue` - Auto-detect type from name on blur
- `src/modules/gear/components/ContainerFormFields.vue` - Add blur event handler

---

## 🎯 Keyword Examples

### Item Categories:
- **water**: water, bottle, canteen, woda, butelka, bidon
- **food**: food, meal, ration, jedzenie, posiłek, racja
- **shelter**: tent, shelter, tarp, namiot, schronienie, plachta
- **fire**: fire, lighter, match, ogień, zapałki, zapalniczka
- **firstAid**: first aid, medical, bandage, apteczka, pierwsza pomoc, bandaż
- **tools**: tool, knife, multitool, narzędzie, nóż, siekiera
- **navigation**: compass, map, gps, kompas, mapa, nawigacja
- **communication**: radio, phone, communication, radio, telefon, komunikacja
- **clothing**: clothing, jacket, pants, odzież, kurtka, spodnie
- **hygiene**: hygiene, soap, toothbrush, higiena, mydło, szczoteczka

### Container Types:
- **backpack**: backpack, rucksack, plecak, tornister
- **bag**: bag, sack, torba, worek
- **pouch**: pouch, pocket, case, pouch, kieszeń, etui
- **box**: box, container, skrzynka, pojemnik
- **cabinet**: cabinet, closet, szafa, szafka
- **vehicle**: vehicle, car, truck, pojazd, samochód
- **shelf**: shelf, rack, półka, regał
- **drawer**: drawer, szuflada
- **case**: case, suitcase, walizka, kufer
- **trunk**: trunk, boot, bagażnik, kufer

---

## ✅ Acceptance Criteria

- [x] Category is automatically detected from item name
- [x] Container type is automatically detected from container name
- [x] Recognition works for both Polish and English keywords
- [x] Only updates when category/type is still at default ("other")
- [x] Only works for new items/containers, not when editing
- [x] User can still manually change category/type
- [x] Recognition is case-insensitive
- [x] Recognition triggers on blur (when user leaves name field), not during typing

---

## 🔗 Related Features

- Default values (FEATURE-004) - works together with default category/type
- Category icons (FEATURE-002) - detected category shows appropriate icon

---

## 💡 Future Enhancements

- Learning from user choices (removed from scope for now)
- More sophisticated matching (fuzzy matching, synonyms)
- User-configurable keywords
- Confidence scoring for matches

