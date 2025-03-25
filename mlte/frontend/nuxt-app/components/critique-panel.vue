<template>
  <div class="critique-panel">
    <UsaAccordion multiselectable>
      <div v-for="(quality, index) in qualities" :key="index">
        <UsaAccordionItem :label="quality.name">
          <div v-if="quality.isMet">
            <span>Pass</span>
          </div>
          <div v-else>
            <span class="fail">Fail</span>
            <ul>
              <li v-for="(critique, idx) in quality.critique" :key="idx">
                <div v-if="critique.requirement">
                  <strong>{{ critique.requirement }}</strong>
                  <ul>
                    <li v-for="(critic, i) in critique.critics" :key="i">
                      {{ i+1 + ": " + critic }}
                    </li>
                  </ul>
                </div>
                <div v-else>
                  <strong>{{ critique.set.join(', ') }}:</strong>
                  <ul>
                    <li v-for="(critic, i) in critique.critics" :key="i">
                      {{ critic }}
                    </li>
                  </ul>
                </div>
              </li>
            </ul>
          </div>
        </UsaAccordionItem>
      </div>
    </UsaAccordion>
  </div>
</template>

<script lang="ts">

interface IndividualCritique {
  requirement: string;
  critiques: string[];
}

interface SetCritique {
  set: string[];
  critiques: string[];
}

interface Quality {
  name: string;
  isMet: boolean;
  critique: IndividualCritique[] | SetCritique[];
}

export default {
  name: 'CritiquePanel',
  props: {
    qualities: {
      type: Array as () => Quality[],
      required: true,
    },
  },
  setup(props) {
    console.log(props.qualities);
    console.log("CritiquePanel");
    console.log(props.qualities[0].critique);
  },
};
</script>

<style scoped>
.critique-panel {
  margin-left: 20px;
  padding: 20px;
}

.quality-section {
  margin-bottom: 20px;
}

.fail {
  color: red;
}

.fail ul {
  padding-left: 20px;
}
</style>
