<template>
    <div class="filter-container">
        <!-- USelectMenu: first level category -->
        <USelectMenu 
            v-model="selectedMainCategory" 
            :options="mainCategories"
            value-attribute="value"
            option-attribute="label"
            multiple
        >
            <template #label>
                <div class="selected-labels">
                    <span v-if="selectedLabels.length === 0">All</span>
                    <span v-else>{{ selectedLabels.join(", ") }}</span>
                </div>
            </template>

            <template #option="{ option }">
                <div class="dropdown-wrapper">
                    <span>{{ option.label }}</span>
                
                    <UDropdown
                        v-if="option.children"
                        mode="hover"
                        :items="generateDropdownItems(option.children)"
                        :popper="{ placement: 'right-start' }"
                    >
                        <UIcon name="i-heroicons-chevron-right-20-solid"/>
                    </UDropdown>
                </div>
            </template>
        </USelectMenu>
    </div>
</template>
  
<script setup>
  
const emit = defineEmits(["update:selected"]);

const mainCategories = ref([
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
      { label: "Robustness", value: "Robustness" }
    ]
  }
]);

const selectedCategories = ref([]);
const selectedMainCategory = ref(null);

const handleSelection = (selected) => {
  if (!selectedCategories.value.includes(selected.value)) {
    selectedCategories.value.push(selected.value);
  } else {
    selectedCategories.value = selectedCategories.value.filter(item => item !== selected.value);
  }

  emit('update:selected', selectedCategories.value);
};

const selectedLabels = computed(() => {
  return selectedCategories.value.map(val => {
    for (const category of mainCategories.value) {
      const found = category.children?.find(child => child.value === val);
      if (found) return found.label;
    }
    return null;
  }).filter(Boolean);
});

const generateDropdownItems = (children) => {
  return [children.map(child => ({
    label: child.label,
    icon: selectedCategories.value.includes(child.value) ? "i-heroicons-check" : "",
    click: () => handleSelection(child)
  }))];
};

console.log("children", mainCategories.value[0].children);

</script>
  
<style scoped>
.filter-container {
  width: 200px;
}

.dropdown-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 10px;
  cursor: pointer;
}

</style>