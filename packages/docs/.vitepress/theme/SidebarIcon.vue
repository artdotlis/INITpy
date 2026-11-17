<!--
SPDX-FileCopyrightText: 2026 Artur Lissin

SPDX-License-Identifier: Unlicense
-->

// SPDX-FileCopyrightText: 2026 Artur Lissin // // SPDX-License-Identifier: Unlicense

<script setup lang="ts">
import { computed } from 'vue';
import { PhCode, PhFile, PhInfo } from '@phosphor-icons/vue';

const props = defineProps<{ name: string }>();
const icons: Record<string, unknown> = { code: PhCode, file: PhFile, info: PhInfo };
const Icon = computed(() => icons[props.name] ?? PhCode);
</script>

<template>
    <div class="sidebar-icon">
        <component :is="Icon" :weight="'regular'" />
    </div>
</template>
