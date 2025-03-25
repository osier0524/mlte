<template>
  <div class="quality-inspection">
    <div class="collapsable-header" @click="isExpanded = !isExpanded">
      <span class="collapsable-title">
        {{ isExpanded ? '▼' : '▶' }} Requirement Quality Inspection
      </span>
      <span class="collapsable-icons">
        <span class="warning">
          <Icon name="mdi:alert-circle-outline" class="icon-warning" />
          {{ Object.keys(critiques.warnings).length }}
        </span>
        <span class="error">
          <Icon name="mdi:close-circle-outline" class="icon-error" />
          {{ Object.keys(critiques.errors).length }}
        </span>
      </span>
    </div>

    <div v-if="isExpanded" class="collapsable-content">
      <p class="warning-title">Warnings (Qualities do not meet the standard):</p>
      <div v-for="(details, quality) in critiques.warnings" :key="quality" class="quality-item">
        <div class="quality-header" @click="toggleQuality(quality)">
          <span>{{ expandedQualities.includes(quality) ? '▼' : '▶' }} {{ quality }}</span>
        </div>
        <ul v-if="expandedQualities.includes(quality)" class="quality-details">
          <li v-for="(critique, index) in details" :key="index">{{ index + 1 }}. {{ critique }}</li>
        </ul>
      </div>

      <p class="error-title">Errors (Qualities are completely unsatisfactory):</p>
      <div v-for="(details, quality) in critiques.errors" :key="quality" class="quality-item">
        <div class="quality-header" @click="toggleQuality(quality)">
          <span>{{ expandedQualities.includes(quality) ? '▼' : '▶' }} {{ quality }}</span>
        </div>
        <ul v-if="expandedQualities.includes(quality)" class="quality-details">
          <li v-for="(critique, index) in details" :key="index">{{ critique }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>


<script setup lang="ts">

interface Critique {
  warnings: Record<string, string[]>;
  errors: Record<string, string[]>;
}
const props = defineProps<{
  critiques: Critique;
}>();

const isExpanded = ref<boolean>(false);
const expandedQualities = ref<string[]>([]);

const toggleQuality = (quality: string) => {
  if (expandedQualities.value.includes(quality)) {
    expandedQualities.value = expandedQualities.value.filter(q => q !== quality);
  } else {
    expandedQualities.value.push(quality);
  }
};
</script>


<style scoped>
.quality-inspection {
  border: 1px solid #000;
  border-radius: 5px;
  padding: 10px; 
}

.collapsable-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.collapsable-title {
  font-weight: bold;
}

.collapsable-icons {
  display: flex;
  align-items: center;
  gap: 10px;
}

.warning, .error {
  display: flex;
  align-items: center;
  gap: 4px;
}

.icon-warning {
  color: gold;
  font-size: 20px;
}

.icon-error {
  color: red;
  font-size: 20px;
}

.collapsable-content {
  margin-top: 10px;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 5px;
}

.warning-title,
.error-title {
  font-weight: bold;
}

.quality-details {
  margin-left: 15px;
  padding-left: 5px;
  border-left: 2px solid #ccc;
}
</style>