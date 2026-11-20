<!--
SPDX-FileCopyrightText: 2026 Artur Lissin

SPDX-License-Identifier: Unlicense
-->

<script setup lang="ts">
import { computed } from 'vue';
import {
    PhDna,
    PhExport,
    PhFlask,
    PhHouse,
    PhInfo,
    PhPill,
    PhPhone,
    PhQuotes,
    PhMagnifyingGlass,
    PhShare,
    PhArchive,
    PhCode,
    PhDatabase,
} from '@phosphor-icons/vue';
import type { IconPreset, IconName } from '@theme/icons';

const registry: Record<IconName, unknown> = {
    info: PhInfo,
    house: PhHouse,
    share: PhShare,
    search: PhMagnifyingGlass,
    database: PhDatabase,
    export: PhExport,
    dna: PhDna,
    pill: PhPill,
    flask: PhFlask,
    archive: PhArchive,
    code: PhCode,
    quotes: PhQuotes,
    phone: PhPhone,
};

const props = defineProps<{ preset: IconPreset }>();
const Icon = computed(() => (registry[props.preset.name] ?? PhInfo) as never);
</script>

<template>
    <div class="sidebar-icon">
        <component :is="Icon" weight="regular" />
    </div>
</template>
