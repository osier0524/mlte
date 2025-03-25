<template>
    <div>
        <br />
            <label><b>Metric Name</b></label>
            <div class="info-container">
                <span class="info-icon">i</span>
                <div class="tooltip">Define the performance metric to evaluate.</div>
            </div>
            <UInput placeholder="e.g., Recall,  F1-Score" v-model="metric" />
            <br />

            <label><b>Minimum Expected Value</b></label>
            <div class="info-container">
                <span class="info-icon">i</span>
                <div class="tooltip">Enter the minimum acceptable accuracy value for the selected metric.</div>
            </div>
            <UInput placeholder="e.g., 0.95" v-model="minExpectedValue" />
            <br />

        <br/>
    </div>

    <div>

    </div>
</template>

<script lang="ts">

    export default {
        name: 'MinAccExpectationForm',
        props: {
            problemType: {
                required: true,
            },
            MLTask: {
                required: true,
            },
            usageContext: {
                required: true,
            },
        },
        setup(props) {
            const metric = ref('');
            const minExpectedValue = ref('');

            return {
                metric,
                minExpectedValue,
            };
        },
    }
</script>

<style scoped>
.AIgeneratedtext{
  background-color: #efe8c7;
}

.info-icon {
  display: inline-block;
  width: 20px;
  height: 20px;
  background-color: black;
  color: white;
  border-radius: 50%;
  text-align: center;
  line-height: 20px;
  font-weight: bold;
  font-family: Arial, cursive;
  font-size: 10px;
  cursor: pointer;
  margin-left: 5px;
  position: relative;
}

.tooltip {
  display: none;
  position: absolute;
  background-color: rgb(0, 0, 0);
  color: rgb(255, 255, 255);
  border: 1px solid #ccc;
  padding: 10px;
  font-size: 12px;
  border-radius: 5px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  width: 200px;
  top: 25px; 
  left: 0;
  z-index: 10;
}

.info-container:hover .tooltip {
  display: block;
}

.info-container {
  position: relative;
  display: inline-block;
}

#cautiontext{
  font-size: 12px;
  font-style: italic;
  text-align: center;
}

.input-button-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}

</style>