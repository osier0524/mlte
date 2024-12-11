<template>
  <div>
    <br />
    <!-- API call -->
    <div class="chatgptcall">
      <p><b>What's Inference Latency?</b> </p>
      <p>
        Inference latency refers to the time taken for a trained model to process an input and generate a prediction. 
        <span class="AIgeneratedtext">{{ response }} </span>
      </p>
    </div>
    <br />
    <!-- <p> <b>What does that mean for your project?</b></p> -->

    
   <p><b>Create a Quality Scenario</b></p>
    <br/>
<div>  
  <!-- 1 Inference Option -->
  <label><b>Inference Option</b></label>
  <div class="info-container">
    <span class="info-icon">i</span>
    <div class="tooltip">
     <span>  {{thirdResponse }}</span>
      
    </div>
  </div>

  <!-- USelect Component -->
  <USelect
    placeholder="Select an option..."
    :options="options"
    icon="i-heroicons-magnifying-glass-20-solid"
    v-model="deploymentInfrastructure"
    @change="handleSelection"
  
  />

  <!-- Conditionally show input field for 'Other' -->
  <br />
  <div v-if="showOtherInput">
    <label for="otherInput"><b>*Specify Other Inference Option</b> </label>
    <UInput v-model="OtherInferenceOption" placeholder="Specify your inference option" style="width: 300px;" />
    <br /> 
  </div>

  <!-- <br/> -->

  <div>
    <!-- Deployment Infrastructure -->
    <label><b>Deployment Infrastructure</b></label>
    <div class="info-container">
      <span class="info-icon">i</span>
      <div class="tooltip">
        {{ fourthResponse }}
      </div>
    </div>

    <!-- Deployment Infrastructure Selection -->
    <USelect
      placeholder="Select an option..."
      :options="secondoptions"
      icon="i-heroicons-magnifying-glass-20-solid"
      v-model="infrastructureDetails"
      @change="handleSelectionDeployment"
    />
    <br /> 

    <!-- Conditionally show input field for Other -->
    <div v-if="showOtherInputDeployment">
      <label for="otherInput"><b>*Specify Other Deployment Infrastructure</b></label>
      <UInput v-model="OtherDeploymentOption" placeholder="Specify your deployment infrastructure" style="width: 300px;" />
      <br /> 
    </div>
   
  </div>

  <!-- <br/> -->

  <!-- <p><b>Specific Requirements</b></p> -->
    <!-- <br/> -->

    <!-- Inference Latency Metrics -->
    <label><b>Average Expected Latency</b></label>
    <div class="info-container">
      <span class="info-icon">i</span>
      <div class="tooltip">{{ExpectedLatencyResponse}}</div>
    </div>
    <div style="display: flex; align-items: center;"> 
    <UInput 
    v-model="averageLatency" 
    style="width: 50px;" 
     />
     <p style="margin-left:8px; margin-bottom:0;">

      <USelect
          placeholder="unit"
          variant="outline"
          :options="['seconds (sec)', 'milliseconds (ms)', 'microseconds (µs)']"
           v-model="unit_averagelatency"
      />
      </p>
     </div>
    <br />


    <div style="display: flex; align-items: flex-start;">
  <!-- Percentage of Requests to Meet Target -->
  <div style="margin-right: 50px;">
    <label><b>Percentage of Requests to Meet Target</b></label>
    <div class="info-container">
      <span class="info-icon">i</span>
      <div class="tooltip">{{ PercenTargetResponse }}</div>
    </div>
    <div style="display: flex; align-items: center;"> 
      <UInput v-model="PercentageLatency" style="width: 50px;" />
      <p style="margin-left:8px; margin-bottom:0;">%</p>
    </div>
  </div>

  <!-- Expected Latency -->
  <div>
    <label><b>Expected Latency</b></label>
    <div class="info-container">
      <span class="info-icon">i</span>
      <div class="tooltip">{{ExpectedLatency}}n</div>
    </div>
    <div style="display: flex; align-items: center;"> 
      <UInput v-model="latencySeconds" style="width: 50px;" />
      <p style="margin-left:8px; margin-bottom:0;">

<USelect
    placeholder="unit"
    variant="outline"
    :options="['seconds (sec)', 'milliseconds (ms)', 'microseconds (µs)']"
    v-model="unit_expectedlatency"
/>
</p>
    </div>
  </div>
</div>

<br/>

      <!-- Dynamic Sentence -->
      <p class="input-group" style="padding-top: 10px; padding-bottom: 10px">
  <b>Scenario for Inference Latency:</b> Model's inference is [{{ firstWordOfDeploymentInfrastructure }}], with an average latency of [{{ averageLatency }}] in [{{unit_averagelatency}}]. [{{ PercentageLatency }} ]% of requests will have a maximum latency of [{{ latencySeconds }}] in [{{ unit_expectedlatency }}]. The model's deployment infrastructure is [{{firstWordOfinfrastructureDetails }}].
</p>
<br/>
<UButton color="yellow" :ui="{ rounded: 'rounded-full' }" @click="checkMetrics" :style="{color: 'black'}" ><b>Do these metrics make sense?</b></UButton>

<br/>
<br/>

<!--  the 2nd call -->
<p v-if="secondResponse && secondResponse.length > 0">
    <ul class="AIgeneratedtext"> 
        <li v-for="(bullet, index) in secondResponse" :key="index" class="spaced-bullet">{{ bullet }}</li>
    </ul>
</p>



<br/>
</div>
</div>


<!-- SAVE BUTTON --> 
<div style="display: flex; align-items: center;">
    <UButton color="yellow" :disabled="!isFormComplete" @click="saveForm" :style="{color: 'black', width: '80px', justifyContent: 'center', alignItems: 'center'}">
        <b>Save</b>
    </UButton>
    <p v-if="saveStatusMessage" style="color: gray; margin-left: 10px; font-size: 14px;">
        {{ saveStatusMessage }}
    </p>
</div>

<br/>

<span class="AIgeneratedtext" id="cautiontext"> Highlighted text was generated by AI. Verify information as ChatGPT can make mistakes </span>


<p> </p>

</template>

<script lang="ts">
import type { _textColor } from '#tailwind-config/theme';
import { ref, onMounted, computed } from 'vue';
import { openai } from '~/composables/openai';

export default {
  data() {
    return {
      selectedOption: '',
      otherOptionValue: '',
      showOtherOption: false,
      OtherDeploymentOption: '',
      infrastructureDetails: '', 
      deploymentInfrastructure: '', // v-model for the select field
      otherInputValue: '', // v-model for the other input field
      showOtherInput: false, // To control the visibility of the input field
      showOtherInputDeployment: false,
      secondoptions: [
        'Cloud (enables scalable, remote access to computational resources and storage for inference)', 
        'On-premise (model runs on local, in-house servers, offering full control over the environment but requiring in-house maintenance)', 
        'Edge (allows real-time predictions and low-latency while minimizing the need for data transmission to centralized servers)', 
        'TBD', 
        'Other'
      ],

      options: [
        'Batch Inference (the model makes predictions on a bunch of common unlabeled examples and then caches those prediction)',
        'Streaming Inference (model only makes predictions on demand)',
        'TBD',
        'Other',
        ],
  
    };
  },

  // METHODS 
  methods: {
    toggleOtherOption() {
      this.showOtherOption = this.selectedOption === 'other';
    },
    handleSelection() {
      // Show the input field if "Other" is selected
      this.showOtherInput = this.deploymentInfrastructure === 'Other';
    },

    handleSelectionDeployment(){
      this.showOtherInputDeployment = this.infrastructureDetails === 'Other';
    }

  },

  // COMPONENT METADATA
  name: 'InferenceLatencyForm',
  props: {
    MLTask: {
      required: true,
    },
    usageContext: {
      required: true,
    },
  },

  // SETUP 
  setup(props) {
    const response = ref('');
    const secondResponse = ref('');
    const thirdResponse = ref('');
    const cleanedText = ref('');
    const fourthResponse = ref('');
    const ExpectedLatencyResponse = ref('');
    const PercenTargetResponse = ref ('');
    const ExpectedLatency = ref ('');
    const unit_averagelatency = ref<string | null>(null);
    const unit_expectedlatency = ref<string | null>(null);
    const deploymentInfrastructure = ref<string | null>(null);
    const infrastructureDetails = ref<string | null>(null);
    const averageLatency = ref<string | null>(null);
    const PercentageLatency = ref<string | null>(null);
    const latencySeconds = ref<string | null>(null);

    // New state for save status
    const saveStatusMessage = ref('');

    // Computed property to check if the form is complete
    const isFormComplete = computed(() => {
        return (
            deploymentInfrastructure.value &&
            infrastructureDetails.value &&
            averageLatency.value &&
            PercentageLatency.value &&
            latencySeconds.value
        );
    });

    const saveForm = () => {
        const formData = {
            deploymentInfrastructure: deploymentInfrastructure.value,
            infrastructureDetails: infrastructureDetails.value,
            averageLatency: averageLatency.value,
            PercentageLatency: PercentageLatency.value,
            latencySeconds: latencySeconds.value,
        };
         // Save to local storage
        localStorage.setItem('formData', JSON.stringify(formData));
        // Simulate saving the data (e.g., make an API call)
        // You can replace this with actual API call logic
        console.log("Saving form data:", formData);
        
        // Set a success message
        saveStatusMessage.value = "Form saved successfully";


    };

    // UTILITY FUNCTIONS
  //   const splitByDash = (text) => {
  //   return text
  //     .split('-')
  //     .map(item => `- ${item.trim()}`) // Keep the "-" character and trim spaces
  //     .filter(Boolean);


  // };

  // COMPUTED PROPERTIES
    //  first word of deploymentInfrastructure and detailsa
    const firstWordOfDeploymentInfrastructure = computed(() => {
      if (deploymentInfrastructure.value) {
        return deploymentInfrastructure.value.split(' ')[0]; 
      }
      return '';
    });

    const firstWordOfinfrastructureDetails = computed(() => {
      if (infrastructureDetails.value) {
        return infrastructureDetails.value.split(' ')[0]; 
      }
      return '';
    });

    // OPEN AI API INTEGRATION

    // FIRST CALL
    const chat_role = 'You are a specialized data scientist with knowledge in both software engineering and data science. Offer thoughful criticism.';

    const getChatResponse = async () => {
      const { chat } = openai();
      try {
        const messages = [
          {
            role: 'system',
            content: chat_role,
          },
          {
            role: 'user',
            content: `Write one sentence to explain the potential consequences of not considering inference latency in the context of ${props.MLTask} and ${props.usageContext}. Use simple language that data scientists would understand`,
          },
        ];

        const chatResponse = await chat(messages, 'gpt-3.5-turbo');
        const splitResponse = chatResponse.split('\n\n');
        response.value = splitResponse[0];
      } catch (error) {
        console.error('Error fetching chat response:', error);
      }
    };


    // Second API call on button click
    const checkMetrics = async () => {
    const { chat } = openai();
    try {
        const messages = [
            {
                role: 'system',
                content: chat_role,
            },
            {
                role: 'user',
                content: `Please review the following latency metrics for ${props.MLTask}:
                - Average Latency: ${averageLatency.value} seconds
                - Percentage of Requests to Meet Target: ${PercentageLatency.value}% requests should meet this latency
                - Latency in Seconds: ${latencySeconds.value} seconds
                - The Inference option for this project is ${deploymentInfrastructure.value}
                - The deployment infrastructure for this project is ${infrastructureDetails.value}

                Do these metrics seem reasonable for this project? Please respond with three brief bullet points:
                - [warning emoji] Average Latency: 
                - [check mark emoji] Percentage of Requests to Meet Target: 
                - [warning emoji] Latency in Seconds: `,
            },
        ];

        const chatResponse = await chat(messages, 'gpt-3.5-turbo');
        
        // Clean the chat response and extract the bullet points
        secondResponse.value = formatSecondResponse(chatResponse);
    } catch (error) {
        console.error('Error fetching metrics response:', error);
    }
};

// Function to format the second API response
function formatSecondResponse(text) {
    // Split the response into lines and filter out empty lines
    const lines = text.split('\n').filter(line => line.trim() !== '');
    
    // Map lines to create a bullet point list and return only the first three items
    const bullets = lines.slice(0, 3).map(line => line.trim());
    
    // Return the formatted output
    return bullets;
}


 // Third API call - info icon
const InfoIcon1 = async () => {
   const { chat } = openai();
   try {
       const messages = [
           {
               role: 'system',
               content: chat_role,
           },
           {
               role: 'user',
               content: `what inference option is recommended for a ${props.MLTask} project that has the following computing resources: 
                 Graphics Processing Units (GPUs): 0 
                 Central Processing Units (CPUs): 1
                 Memory: 6MiB
                 Storage: 2KiB

                 The inference options provided are: stream inference, batch inference or other. Provide only a one sentence recommendation.
               `,
           },
       ];

       const thirdchatResponse = await chat(messages, 'gpt-3.5-turbo');
       thirdResponse.value = thirdchatResponse;


   } catch (error) {
       console.error('Error fetching InfoIcon1 response:', error);
   }
};

// 4th API call - info icon
const InfoIcon2 = async () => {
   const { chat } = openai();
   try {
       const messages = [
           {
               role: 'system',
               content: chat_role,
           },
           {
               role: 'user',
               content: `what deployment infrastructure is recommended for a ${props.MLTask} project that has the following computing resources: 
                 Graphics Processing Units (GPUs): 0 
                 Central Processing Units (CPUs): 1
                 Memory: 6MiB
                 Storage: 2KiB

                 The deployment infrastructures provided are: edge, on-premise, cloud, or other. Provide only a one sentence recommendation.
               `,
           },
       ];

       const fourthchatResponse = await chat(messages, 'gpt-3.5-turbo');
       fourthResponse.value = fourthchatResponse;

   } catch (error) {
       console.error('Error fetching InfoIcon2 response:', error);
   }
};

// 5th API call - info icon Expected Latency

const InfoIconExpectedLatency = async () => {
   const { chat } = openai();
   try {
       const messages = [
           {
               role: 'system',
               content: chat_role,
           },
           {
               role: 'user',
               content: `what average expected latency is recommended for a ${props.MLTask} project that has the following computing resources: 
                 Graphics Processing Units (GPUs): 0 
                 Central Processing Units (CPUs): 1
                 Memory: 6MiB
                 Storage: 2KiB
                
                Consider product and deployment factors: ${props.usageContext}. Provide only a one sentence recommendation.
               `,
           },
       ];

       const chatexpectedLatency = await chat(messages, 'gpt-3.5-turbo');
       ExpectedLatencyResponse.value = chatexpectedLatency;

   } catch (error) {
       console.error('Error fetching InfoIconExpectedLatency response:', error);
   }
};


// 6th API call - info icon Percentage of Requests

const InfoIconPercenTarget = async () => {
   const { chat } = openai();
   try {
       const messages = [
           {
               role: 'system',
               content: chat_role,
           },
           {
               role: 'user',
               content: `what percentage of requests target to meet is recommended, besides the average, for a ${props.MLTask} project that has the following computing resources: 
                 Graphics Processing Units (GPUs): 0 
                 Central Processing Units (CPUs): 1
                 Memory: 6MiB
                 Storage: 2KiB
                
                Consider product and deployment factors. Provide only a one sentence recommendation with a percentage range you recommend to consider given the production computing resources. Do not mention use first person language.
               `,
           },
       ];

       const chatTarget = await chat(messages, 'gpt-3.5-turbo');
       PercenTargetResponse.value = chatTarget;

   } catch (error) {
       console.error('Error fetching InfoIconPercenTarget response:', error);
   }
};

// 7th API call - info icon expected latency

const InfoIconLatency = async () => {
   const { chat } = openai();
   try {
       const messages = [
           {
               role: 'system',
               content: chat_role,
           },
           {
               role: 'user',
               content: `what expected latency to is recommended, considering ${PercentageLatency} for a ${props.MLTask} project that has the following computing resources: 
                 Graphics Processing Units (GPUs): 0 
                 Central Processing Units (CPUs): 1
                 Memory: 6MiB
                 Storage: 2KiB
                
                Consider product and deployment factors: ${props.usageContext}. Provide only a one sentence recommendation with a latency recommendation for the percentage they provided. Do not mention use first person language.
               `,
           },
       ];

       const chatinfoExpectedLatency = await chat(messages, 'gpt-3.5-turbo');
       ExpectedLatency.value = chatinfoExpectedLatency;

   } catch (error) {
       console.error('Error fetching InfoIconExpectedLatency response:', error);
   }
};





    // HOOK
    onMounted(() => {
      getChatResponse(); // initial call 
      InfoIcon1(); // info icon calls
      InfoIcon2();
      InfoIconLatency();
      InfoIconPercenTarget();
      InfoIconExpectedLatency();
  
        // Load data from local storage
        const storedData = localStorage.getItem('formData');
        if (storedData) {
        const formData = JSON.parse(storedData);
        deploymentInfrastructure.value = formData.deploymentInfrastructure;
        infrastructureDetails.value = formData.infrastructureDetails;
        averageLatency.value = formData.averageLatency;
        PercentageLatency.value = formData.PercentageLatency;
        latencySeconds.value = formData.latencySeconds;
    }
    });

    return {
      response,
      secondResponse,
      thirdResponse,
      fourthResponse,
      ExpectedLatencyResponse,
      deploymentInfrastructure,
      infrastructureDetails,
      ExpectedLatency,
      cleanedText,
      averageLatency,
      PercentageLatency,
      latencySeconds,
      unit_averagelatency,
      unit_expectedlatency,
      firstWordOfDeploymentInfrastructure, 
      firstWordOfinfrastructureDetails,
      PercenTargetResponse,
      checkMetrics,
      //splitByDash,
      saveStatusMessage,   
      isFormComplete,      
      saveForm,  
    };
  },
};
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
  background-color: #efe8c7;
}
.spaced-bullet {
  margin-bottom: 10px; 
}
.highlighted-bullet {
  background-color: #f0f8ff; 
  padding: 10px;         
  border-radius: 5px;       
  margin-bottom: 10px;     
  font-weight: bold;        
  color: #333;              
  box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
}
</style>