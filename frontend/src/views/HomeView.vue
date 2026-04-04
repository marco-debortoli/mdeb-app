<script setup lang="ts">
import TasksWidget from "@/modules/tasks/TasksWidget.vue";
import JournalWidget from "@/modules/journal/JournalWidget.vue";
import TimeWidget from "@/modules/time_tracking/TimeWidget.vue";
import FinanceWidget from "@/modules/finance/FinanceWidget.vue";
import HealthWidget from "@/modules/health/HealthWidget.vue";
</script>

<template>
  <div class="max-w-6xl mx-auto pb-24 md:pb-6">
    <div class="mb-6">
      <h1 class="text-2xl font-semibold text-slate-800">Welcome, Marco DeBortoli</h1>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-5 items-stretch">
      <TasksWidget />
      <JournalWidget />
      <TimeWidget />
      <FinanceWidget />
      <HealthWidget />
    </div>
  </div>
</template>
