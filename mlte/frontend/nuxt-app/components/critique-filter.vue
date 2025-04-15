<template>
  <div class="critique-filter">
    <div class="filter-container" ref="filterContainer">
      <div class="filter-header" @click="toggleDropdown">
        <span class="filter-label">Filter:</span>
        <div class="selected-values">
          <span v-if="selectedOptions.length === 0">All</span>
          <span v-else>{{ formattedSelection }}</span>
        </div>
        <UIcon :name="isOpen ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'" class="dropdown-icon" />
      </div>

      <div v-if="isOpen" class="dropdown-panel">
        <div class="category-group-label">Select filters:</div>
        <div 
          v-for="category in categories" 
          :key="category.value"
          class="category-item"
        >
          <div class="category-header" @click="toggleCategory(category.value)">
            <span>{{ category.label }}</span>
            <UIcon :name="activeCategory === category.value ? 'i-heroicons-chevron-down' : 'i-heroicons-chevron-right'" />
          </div>

          <div 
            v-show="activeCategory === category.value"
            class="subcategory-list"
          >
            <div 
              v-for="option in category.children" 
              :key="option.value"
              class="option-item"
              @click.stop="toggleOption(option.value)"
            >
              <span>{{ option.label }}</span>
              <UIcon v-if="isSelected(option.value)" name="i-heroicons-check" class="check-icon" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['update:modelValue', 'update:selected']);

// Data
const isOpen = ref(false);
const activeCategory = ref(null);
const filterContainer = ref(null);
const selectedOptions = ref(props.modelValue || []);

// Categories data
const categories = ref([
  {
    label: "Requirement Types",
    value: "requirement-types",
    children: [
      { label: "Functional", value: "Functional" },
      { label: "Non-Functional", value: "Non-Functional" }
    ]
  },
  {
    label: "Quality Attributes",
    value: "quality-attributes",
    children: [
      { label: "Accuracy", value: "Accuracy" },
      { label: "Performance", value: "Performance" },
      { label: "Robustness", value: "Robustness" },
      { label: "Security", value: "Security" },
      { label: "Reliability", value: "Reliability" },
      { label: "Maintainability", value: "Maintainability" }
    ]
  }
]);

// Methods
const toggleDropdown = () => {
  isOpen.value = !isOpen.value;
  // Set active category to first one when opening dropdown
  if (isOpen.value && categories.value.length > 0) {
    activeCategory.value = activeCategory.value || categories.value[0].value;
  }
};

const toggleCategory = (categoryValue) => {
  // Toggle category - if already active, close it, otherwise open it
  activeCategory.value = activeCategory.value === categoryValue ? null : categoryValue;
};

const toggleOption = (optionValue) => {
  if (isSelected(optionValue)) {
    selectedOptions.value = selectedOptions.value.filter(val => val !== optionValue);
  } else {
    selectedOptions.value.push(optionValue);
  }
  
  emit('update:modelValue', selectedOptions.value);
  emit('update:selected', selectedOptions.value);
};

const isSelected = (optionValue) => {
  return selectedOptions.value.includes(optionValue);
};

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (filterContainer.value && !filterContainer.value.contains(event.target)) {
    isOpen.value = false;
  }
};

// Format the selected options to display
const formattedSelection = computed(() => {
  if (selectedOptions.value.length === 0) return 'All';
  
  const labels = [];
  for (const value of selectedOptions.value) {
    for (const category of categories.value) {
      const found = category.children.find(child => child.value === value);
      if (found) {
        labels.push(found.label);
        break;
      }
    }
  }
  
  return labels.sort().join(', ');
});

// Lifecycle hooks
onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.critique-filter {
  width: 100%;
  max-width: 400px;
  position: relative;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.filter-container {
  position: relative;
  width: 100%;
}

.filter-header {
  display: flex;
  align-items: flex-start;
  padding: 10px 12px;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  min-height: 40px;
}

.filter-header:hover {
  border-color: #cbd5e1;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.filter-label {
  font-weight: 600;
  color: #4a5568;
  margin-right: 8px;
}

.selected-values {
  flex: 1;
  overflow-wrap: break-word;
  word-wrap: break-word;
  word-break: break-word;
  color: #2d3748;
  font-size: 0.9rem;
  max-height: 60px;
  overflow-y: auto;
}

.dropdown-icon {
  margin-left: 8px;
  color: #718096;
}

.dropdown-panel {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  width: 100%;
  background-color: white;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 100;
  border: 1px solid #e2e8f0;
  max-height: 300px;
  overflow-y: auto;
  padding: 8px;
}

.category-group-label {
  font-size: 0.8rem;
  color: #718096;
  margin-bottom: 8px;
  padding: 0 8px;
}

.category-item {
  position: relative;
  border-bottom: 1px solid #f1f5f9;
}

.category-item:last-child {
  border-bottom: none;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  color: #1a202c;
  font-weight: 600;
  background-color: #f1f5f9;
  border-radius: 4px;
  margin: 4px 0;
}

.category-header:hover {
  background-color: #e2e8f0;
}

.subcategory-list {
  padding: 5px 5px 5px 25px;
  background-color: #ffffff;
  border-top: 1px solid #e2e8f0;
  border-bottom: 1px solid #e2e8f0;
  margin: 0 0 5px 0;
  border-radius: 0 0 4px 4px;
}

.option-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  margin: 4px 0;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #4a5568;
  border-radius: 4px;
  background-color: #f8fafc;
  position: relative;
}

.option-item:hover {
  background-color: #edf2f7;
}

.check-icon {
  color: #d8ac16;
  font-size: 1.2rem;
}
</style>