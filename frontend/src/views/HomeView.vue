<script setup lang="ts">
import TasksHomeWidget from "@/modules/tasks/widgets/TasksHomeWidget.vue";
import JournalHomeWidget from "@/modules/journal/widgets/JournalHomeWidget.vue";
import TimeHomeWidget from "@/modules/time_tracking/widgets/TimeHomeWidget.vue";
import FinanceHomeWidget from "@/modules/finance/widgets/FinanceHomeWidget.vue";
import HealthHomeWidget from "@/modules/health/widgets/HealthHomeWidget.vue";
</script>

<template>
  <div class="max-w-6xl mx-auto pb-24 md:pb-6">
    <div class="mb-6">
      <h1 class="text-2xl font-semibold text-slate-800">Welcome, Marco DeBortoli</h1>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-5 items-stretch">
      <TasksHomeWidget />
      <JournalHomeWidget />
      <TimeHomeWidget />
      <FinanceHomeWidget />
      <HealthHomeWidget />
    </div>
  </div>
</template>
