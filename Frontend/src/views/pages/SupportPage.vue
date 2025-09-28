<template>
  <div class="w-full h-full p-6">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-semibold text-white mb-2">Support</h1>
      <p class="text-gray-400">Get help and support for your Energy Management System</p>
    </div>

    <!-- Support Sections -->
    <div class="space-y-6">
      <!-- Contact Information -->
      <div class="bg-transparent rounded-lg p-6 border border-gray-600/50">
        <!-- <div class="flex items-center gap-3 mb-6">
          <i class="pi pi-phone text-orange-500 text-xl"></i>
          <h2 class="text-xl font-semibold text-white">Contact Information</h2>
        </div> -->
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-4">
            <div class="flex gap-3">
              <i class="pi mt-1 pi-envelope text-orange-500"></i>
              <div>
                <p class="text-white font-medium">Email Support</p>
                <p class="text-gray-400 text-sm">support@innovx-ems.com</p>
              </div>
            </div>
            
            <div class="flex gap-3">
              <i class="pi mt-1 pi-phone text-orange-500"></i>
              <div>
                <p class="text-white font-medium">Phone Support</p>
                <p class="text-gray-400 text-sm">+212 5-34-03-02-72</p>
              </div>
            </div>
            
            <div class="flex gap-3">
              <i class="pi mt-1 pi-clock text-orange-500"></i>
              <div>
                <p class="text-white font-medium">Business Hours</p>
                <p class="text-gray-400 text-sm">Monday - Friday: 8:00 AM - 6:00 PM</p>
              </div>
            </div>
          </div>
          
          <div class="space-y-4">
            <div class="flex gap-3">
              <i class="pi mt-1 pi-map-marker text-orange-500"></i>
              <div>
                <p class="text-white font-medium">Office Address</p>
                <p class="text-gray-400 text-sm">Lot 660, Hay Moulay Rachid Ben Guerir<br>43150, Morocco</p>
              </div>
            </div>
            
            <div class="flex gap-3">
              <i class="pi mt-1 pi-globe text-orange-500"></i>
              <div>
                <p class="text-white font-medium">Website</p>
                <p class="text-gray-400 text-sm">www.innovx.ma</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- FAQ Section -->
      <div class="bg-transparent rounded-lg p-6 border border-gray-600/50">
        <div class="flex gap-3 mb-6">
          <i class="pi mt-6 pi-question-circle text-orange-500 text-xl"></i>
          <h2 class="text-xl font-semibold text-white">Frequently Asked Questions</h2>
        </div>
        
        <div class="space-y-4">
          <div 
            v-for="(faq, index) in faqs"
            :key="index"
            class="bg-gray-800/30 rounded-lg p-4 border border-gray-700/30"
          >
            <button
              @click="toggleFaq(index)"
              class="w-full flex items-center justify-between text-left"
            >
              <h3 class="font-medium text-white">{{ faq.question }}</h3>
              <i 
                :class="[
                  'pi transition-transform',
                  expandedFaqs.includes(index) ? 'pi-chevron-up' : 'pi-chevron-down',
                  'text-orange-500'
                ]"
              ></i>
            </button>
            <div 
              v-if="expandedFaqs.includes(index)"
              class="mt-3 text-gray-400 text-sm leading-relaxed"
            >
              {{ faq.answer }}
            </div>
          </div>
        </div>
      </div>

      <!-- Documentation Links -->
      <div class="bg-transparent rounded-lg p-6 border border-gray-600/50">
        <div class="flex gap-3 mb-6">
          <i class="pi mt-6 pi-book text-orange-500 text-xl"></i>
          <h2 class="text-xl font-semibold text-white">Documentation</h2>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div 
            v-for="doc in documentation"
            :key="doc.title"
            class="bg-gray-800/30 rounded-lg p-4 border border-gray-700/30 hover:border-gray-600/50 transition-colors cursor-pointer"
          >
            <div class="flex gap-3 mb-2">
              <i :class="[doc.icon, 'text-orange-500 mt-9']"></i>
              <h3 class="font-medium text-white">{{ doc.title }}</h3>
            </div>
            <p class="text-gray-400 text-sm">{{ doc.description }}</p>
          </div>
        </div>
      </div>

      <!-- System Status -->
      <div class="bg-transparent rounded-lg p-6 border border-gray-600/50">
        <div class="flex center gap-3 mb-6">
          <i class="pi mt-6 pi-shield text-orange-500 text-xl"></i>
          <h2 class="text-xl font-semibold text-white">System Status</h2>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="bg-gray-800/30 rounded-lg p-4 border border-gray-700/30">
            <div class="flex items-center gap-3 mb-2">
              <div class="w-3 h-3 bg-green-500 rounded-full"></div>
              <h3 class="font-medium text-white">API Services</h3>
            </div>
            <p class="text-gray-400 text-sm">All systems operational</p>
          </div>
          
          <div class="bg-gray-800/30 rounded-lg p-4 border border-gray-700/30">
            <div class="flex items-center gap-3 mb-2">
              <div class="w-3 h-3 bg-green-500 rounded-full"></div>
              <h3 class="font-medium text-white">Database</h3>
            </div>
            <p class="text-gray-400 text-sm">Connected and healthy</p>
          </div>
          
          <div class="bg-gray-800/30 rounded-lg p-4 border border-gray-700/30">
            <div class="flex items-center gap-3 mb-2">
              <div class="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <h3 class="font-medium text-white">Maintenance</h3>
            </div>
            <p class="text-gray-400 text-sm">Scheduled for next week</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// FAQ data
const faqs = [
  {
    question: "How do I reset my password?",
    answer: "To reset your password, click on the 'Forgot Password' link on the login page and follow the instructions sent to your email address."
  },
  {
    question: "How can I add new meters to the system?",
    answer: "New meters can be added through the Settings page. Navigate to Settings > Smart Meters and use the 'Add New Meter' option."
  },
  {
    question: "What should I do if a meter shows as disconnected?",
    answer: "If a meter shows as disconnected, first check the physical connection. If the issue persists, contact our technical support team."
  },
  {
    question: "How often is the data updated?",
    answer: "Data is updated in real-time for most metrics. Historical data is refreshed every 15 minutes for optimal performance."
  },
  {
    question: "Can I export my data?",
    answer: "Yes, you can export data in CSV format from the Reports page. Click the 'Export CSV' button on any report."
  },
  {
    question: "What browsers are supported?",
    answer: "Our system supports all modern browsers including Chrome, Firefox, Safari, and Edge. We recommend using the latest version for the best experience."
  }
]

// Documentation links
const documentation = [
  {
    title: "User Manual",
    icon: "pi pi-file",
    description: "Complete guide to using the EMS system"
  },
  {
    title: "API Documentation",
    icon: "pi pi-code",
    description: "Technical documentation for developers"
  },
  {
    title: "Installation Guide",
    icon: "pi pi-download",
    description: "Step-by-step installation instructions"
  },
  {
    title: "Troubleshooting",
    icon: "pi pi-wrench",
    description: "Common issues and solutions"
  },
  {
    title: "Video Tutorials",
    icon: "pi pi-video",
    description: "Visual guides and walkthroughs"
  },
  {
    title: "Release Notes",
    icon: "pi pi-info-circle",
    description: "Latest updates and new features"
  }
]

// FAQ expansion state
const expandedFaqs = ref([])

// Toggle FAQ expansion
const toggleFaq = (index) => {
  const expandedIndex = expandedFaqs.value.indexOf(index)
  if (expandedIndex > -1) {
    expandedFaqs.value.splice(expandedIndex, 1)
  } else {
    expandedFaqs.value.push(index)
  }
}
</script>


