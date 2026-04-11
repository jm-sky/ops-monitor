<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useGear } from '../composables/useGear'
import { GearRoutePath } from '../routes'
import { getActionIcon } from '../utils/actionIcons'

// Action icons
const MoreActionsIcon = getActionIcon('moreActions')
const CreateIcon = getActionIcon('create')
const ImportFromMarkdownIcon = getActionIcon('importFromMarkdown')
const ExportAllToMarkdownIcon = getActionIcon('exportAllToMarkdown')
const ExportToCSVIcon = getActionIcon('exportToCSV')
const DeleteAllIcon = getActionIcon('deleteAll')

const router = useRouter()
const { t } = useI18n()
const { containers, deleteAllContainers } = useGear()

const emit = defineEmits<{
  exportAllToMarkdown: [],
  exportAllToCSV: [],
  import: [],
}>()

const handleCreate = () => {
  router.push(GearRoutePath.ContainerNew)
}

const handleImport = () => {
  emit('import')
}

const handleDeleteAll = () => {
  if (confirm(t('gear.container.deleteAllConfirm'))) {
    try {
      deleteAllContainers()
      toast.success(t('gear.container.deleteAllSuccess'))
    } catch {
      toast.error(t('common.error'))
    }
  }
}

const handleExportAllToMarkdown = () => {
  emit('exportAllToMarkdown')
}

const handleExportAllToCSV = () => {
  emit('exportAllToCSV')
}
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button
        v-tooltip.bottom="t('gear.actions.moreActions')"
        variant="ghost"
        size="sm"
        class="sm:shrink-0"
        :aria-label="t('gear.actions.moreActions')"
      >
        <MoreActionsIcon class="size-4" />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end">
      <DropdownMenuItem @click="handleCreate">
        <CreateIcon class="size-4 mr-2" />
        {{ t('gear.container.create.new') }}
      </DropdownMenuItem>
      <DropdownMenuItem @click="handleImport">
        <ImportFromMarkdownIcon class="size-4 mr-2" />
        {{ t('gear.import.fromMarkdown') }}
      </DropdownMenuItem>
      <DropdownMenuSeparator v-if="containers.length > 0" />
      <DropdownMenuItem
        v-if="containers.length > 0"
        @click="handleExportAllToMarkdown"
      >
        <ExportAllToMarkdownIcon class="size-4 mr-2" />
        {{ t('gear.export.allToMarkdown') }}
      </DropdownMenuItem>
      <DropdownMenuItem
        v-if="containers.length > 0"
        @click="handleExportAllToCSV"
      >
        <ExportToCSVIcon class="size-4 mr-2" />
        {{ t('gear.export.allToCSV') }}
      </DropdownMenuItem>
      <DropdownMenuSeparator v-if="containers.length > 0" />
      <DropdownMenuItem
        v-if="containers.length > 0"
        class="text-destructive focus:text-destructive"
        @click="handleDeleteAll"
      >
        <DeleteAllIcon class="size-4 mr-2" />
        {{ t('gear.container.deleteAll') }}
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>
