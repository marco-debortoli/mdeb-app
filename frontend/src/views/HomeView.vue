<script setup lang="ts">
import TasksWidget from "@/components/home/TasksWidget.vue";
import JournalWidget from "@/components/home/JournalWidget.vue";
import TimeWidget from "@/components/home/TimeWidget.vue";
import FinanceWidget from "@/components/home/FinanceWidget.vue";
import HealthWidget from "@/components/home/HealthWidget.vue";
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
