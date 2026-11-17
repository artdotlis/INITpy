<!--
SPDX-FileCopyrightText: 2026 Artur Lissin

SPDX-License-Identifier: Unlicense
-->

<script setup lang="ts">
import { computed } from 'vue';
import {
    PhArchive,
    PhBookOpen,
    PhChartBar,
    PhCode,
    PhCpu,
    PhCube,
    PhDatabase,
    PhFile,
    PhFunction,
    PhGear,
    PhGitBranch,
    PhGlobe,
    PhInfo,
    PhKey,
    PhPulse,
    PhRocket,
    PhShieldCheck,
    PhStar,
    PhTerminal,
    PhTrophy,
    PhUsers,
    PhWrench,
} from '@phosphor-icons/vue';

// Keys match the `Icon` constants in ./icons.ts (selected in config).
const registry = {
    code: PhCode,
    file: PhFile,
    info: PhInfo,
    book: PhBookOpen,
    terminal: PhTerminal,
    gear: PhGear,
    cpu: PhCpu,
    database: PhDatabase,
    gitBranch: PhGitBranch,
    function: PhFunction,
    cube: PhCube,
    wrench: PhWrench,
    shield: PhShieldCheck,
    key: PhKey,
    pulse: PhPulse,
    chart: PhChartBar,
    rocket: PhRocket,
    globe: PhGlobe,
    star: PhStar,
    users: PhUsers,
    trophy: PhTrophy,
    archive: PhArchive,
};

const props = defineProps<{ name: string }>();
const Icon = computed(() => registry[props.name] ?? PhCode);
</script>

<template>
    <div class="sidebar-icon">
        <component :is="Icon" weight="regular" />
    </div>
</template>
