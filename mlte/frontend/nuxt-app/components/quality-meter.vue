<template>
    <div class="quality-meter">
        <h3 class="font-bold">{{ title }}</h3>
        <p class="text-sm text-gray-500">{{ summary }}</p>
        <div class="flex items-center mt-2">
        <input 
            type="range" 
            :value="percentage" 
            min="0" 
            max="100" 
            class="slider"
            disabled
        />
        <span class="ml-2 font-medium">{{ percentage }}%</span>
        </div>
    </div>
    <ProgressBar :value="percentage"></ProgressBar>
</template>

<script setup>
import ProgressBar from 'primevue/progressbar';

defineProps({
  title: String,
  summary: String,
  percentage: Number,
});
</script>

<style scoped>
.quality-meter {
  margin-bottom: 16px;
}
.slider {
  width: 150px;
  appearance: none;
  background: yellow;
  height: 6px;
  border-radius: 3px;
}
.slider::-webkit-slider-thumb {
  appearance: none;
  width: 16px;
  height: 16px;
  background: lightgrey;
  border-radius: 50%;
  cursor: pointer;
}
</style>


