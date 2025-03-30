
<template>
    <div class="min-h-full">
      <Disclosure as="nav" class="border-b border-gray-200 bg-white" v-slot="{ open }">
        <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div class="flex h-16 justify-between">
            <div class="flex">
              
              <div class="hidden sm:-my-px sm:ml-6 sm:flex sm:space-x-8">
                <a
                  v-for="item in navigation"
                  :key="item.name"
                  href="#"
                  @click.prevent="setTab(item)"
                  :class="[item.current ? 'border-indigo-500 text-gray-900' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700', 'inline-flex items-center border-b-2 px-1 pt-1 text-sm font-medium']"
                >
                  {{ item.name }}
                </a>
              </div>
            </div>
            <div class="hidden sm:ml-6 sm:flex sm:items-center">
              <button type="button" class="relative rounded-full bg-white p-1 text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
                <span class="absolute -inset-1.5"></span>
                <span class="sr-only">View notifications</span>
                <BellIcon class="size-6" aria-hidden="true" />
              </button>
              <!-- Profile dropdown -->
              <Menu as="div" class="relative ml-3">
                <div>
                  <MenuButton class="relative flex max-w-xs items-center rounded-full bg-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
                    <span class="absolute -inset-1.5"></span>
                    <span class="sr-only">Open user menu</span>
                    <img class="size-8 rounded-full" :src="user.imageUrl" alt="" />
                  </MenuButton>
                </div>
                <transition
                  enter-active-class="transition ease-out duration-200"
                  enter-from-class="transform opacity-0 scale-95"
                  enter-to-class="transform opacity-100 scale-100"
                  leave-active-class="transition ease-in duration-75"
                  leave-from-class="transform opacity-100 scale-100"
                  leave-to-class="transform opacity-0 scale-95"
                >
                  <MenuItems class="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-white py-1 shadow-lg ring-1 ring-black/5 focus:outline-none">
                    <MenuItem v-for="item in userNavigation" :key="item.name" v-slot="{ active }">
                      <a :href="item.href" :class="[active ? 'bg-gray-100 outline-none' : '', 'block px-4 py-2 text-sm text-gray-700']">{{ item.name }}</a>
                    </MenuItem>
                  </MenuItems>
                </transition>
              </Menu>
            </div>
            <div class="-mr-2 flex items-center sm:hidden">
              <!-- Mobile menu button -->
              <DisclosureButton class="relative inline-flex items-center justify-center rounded-md bg-white p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
                <span class="absolute -inset-0.5"></span>
                <span class="sr-only">Open main menu</span>
                <Bars3Icon v-if="!open" class="block size-6" aria-hidden="true" />
                <XMarkIcon v-else class="block size-6" aria-hidden="true" />
              </DisclosureButton>
            </div>
          </div>
        </div>
  
        <DisclosurePanel class="sm:hidden">
          <div class="space-y-1 pb-3 pt-2">
            <DisclosureButton
              v-for="item in navigation"
              :key="item.name"
              as="a"
              href="#"
              @click.prevent="setTab(item)"
              :class="[item.current ? 'border-indigo-500 bg-indigo-50 text-indigo-700' : 'border-transparent text-gray-600 hover:border-gray-300 hover:bg-gray-50 hover:text-gray-800', 'block border-l-4 py-2 pl-3 pr-4 text-base font-medium']"
            >
              {{ item.name }}
            </DisclosureButton>
          </div>
          <div class="border-t border-gray-200 pb-3 pt-4">
            <div class="flex items-center px-4">
              <div class="shrink-0">
                <img class="size-10 rounded-full" :src="user.imageUrl" alt="" />
              </div>
              <div class="ml-3">
                <div class="text-base font-medium text-gray-800">{{ user.name }}</div>
                <div class="text-sm font-medium text-gray-500">{{ user.email }}</div>
              </div>
              <button type="button" class="relative ml-auto shrink-0 rounded-full bg-white p-1 text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
                <span class="absolute -inset-1.5"></span>
                <span class="sr-only">View notifications</span>
                <BellIcon class="size-6" aria-hidden="true" />
              </button>
            </div>
            <div class="mt-3 space-y-1">
              <DisclosureButton
                v-for="item in userNavigation"
                :key="item.name"
                as="a"
                :href="item.href"
                class="block px-4 py-2 text-base font-medium text-gray-500 hover:bg-gray-100 hover:text-gray-800"
              >
                {{ item.name }}
              </DisclosureButton>
            </div>
          </div>
        </DisclosurePanel>
      </Disclosure>
  
      <div class="py-10">
        <header>
          <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <!-- The header now reflects the currently selected tab -->
            <h1 class="text-3xl font-bold tracking-tight text-gray-900">{{ currentTab.name }}</h1>
          </div>
        </header>
        <main>
          <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
            <!-- Conditional content based on the current tab -->
            <div v-if="currentTab.name === 'Overview'">
              <p>This is the overview of your OCR video analysis service. Here you can see summaries and performance metrics.</p>
            </div>
            <div v-else-if="currentTab.name === 'Save Video'">
              <p>Choose a video to save</p>

              <!--- SAVE VIDEO HERE-->
              <div class="grid grid-cols-1 gap-y-4 sm:grid-cols-2 sm:gap-x-6 sm:gap-y-10 lg:grid-cols-3 lg:gap-x-8">
                <div v-for="video in videos" :key="video.id" class="group relative flex flex-col overflow-hidden rounded-lg border border-gray-200 bg-white">
                  <video controls class="w-full h-auto" :src="video.videoSrc" playsinline
                  webkit-playsinline  preload controlsList="nofullscreen">
                    <source type="video/mp4" :poster="video.poster" >
                    Your browser does not support the video tag.
                    
                  </video>
                  
                  <div class="flex flex-1 flex-col space-y-2 p-4">
                    <h3 class="text-sm font-medium text-gray-900">
                      <a  :href="video.videoSrc"> 
                        {{ video.title }}</a>                                 
                    </h3>
                    <p class="text-sm text-gray-500">{{ video.description }}</p>
                    <div class="flex flex-1 flex-col justify-end">
                      <p class="text-sm italic text-gray-500">{{ video.date_published }}</p>
                      <button type="button" @click.stop="saveVideo(video.id)" class="flex w-1/2 items-center justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">Save</button>
                  </div>
                    
                  </div>
                </div>
              </div>
            </div>
            <div v-else-if="currentTab.name === 'Categories'">
              <!-- Dynamic Category Tabs -->
              <div class="flex space-x-4 mb-4">
                <button
                  v-for="cat in categories"
                  :key="cat.name"
                  @click="setCategory(cat)"
                  :class="[cat.current ? 'border-indigo-500 text-gray-900' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700', 'px-3 py-2 text-sm font-medium border-b-2']">
                  {{ cat.name }}
                </button>
              </div>
              
              <!-- Grid of Video Cards for the Selected Category -->
              <div class="grid grid-cols-1 gap-y-4 sm:grid-cols-2 sm:gap-x-6 sm:gap-y-10 lg:grid-cols-3 lg:gap-x-8">
                <div
                  v-for="video in filteredVideos"
                  :key="video.id"
                  class="group relative flex flex-col overflow-hidden rounded-lg border border-gray-200 bg-white">
                  
                  <video controls class="w-full h-auto" :src="video.videoSrc" playsinline webkit-playsinline preload controlsList="nofullscreen">
                    <source type="video/mp4" :poster="video.poster">
                    Your browser does not support the video tag.
                  </video>
                  
                  <div class="flex flex-1 flex-col space-y-2 p-4">
                    <h3 class="text-sm font-medium text-gray-900">
                      <a :href="video.videoSrc"> {{ video.title }} </a>
                    </h3>
                    <p class="text-sm text-gray-500">{{ video.description }}</p>
                    <div class="flex flex-1 flex-col justify-end">
                      <p class="text-sm italic text-gray-500">{{ video.date_published }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

           
            <div v-else-if="currentTab.name === 'Recommendations'">
              <p>View recommendations based on your video analysis. Get insights and tips to improve your video content.</p>
              
            </div>
            <div v-else-if="currentTab.name === 'Shared Albums'">
              <p>Share videos with your friends!</p>
              
            </div>
          </div>
        </main>
      </div>
    </div>
</template>
  
<script setup>
import { ref, onMounted,reactive, computed } from 'vue'
import { Disclosure, DisclosureButton, DisclosurePanel, Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'
import { Bars3Icon, BellIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import metadata from '../assets/videoMetadata.json';
import axios from 'axios';

// Category code

const categories = reactive([
  { name: 'Action', current: true },
  { name: 'Drama', current: false },
  { name: 'Comedy', current: false },
]);


const currentCategory = ref(categories[0]);

function setCategory(category) {
  currentCategory.value = category;
  categories.forEach(cat => cat.current = (cat.name === category.name));
}


const user = {
  name: 'Poskitt',
  email: 'tom@example.com',
  imageUrl:
    'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
}



const navigation = reactive([
{ name: 'Overview', href: '#', current: true },
{ name: 'Save Video', href: '#', current: false },
{ name: 'Categories', href: '#', current: false },
{ name: 'Recommendations', href: '#', current: false },
{ name: 'Shared Albums', href: '#', current: false },
])

const userNavigation = [
  { name: 'Your Profile', href: '#' },
  { name: 'Settings', href: '#' },
  { name: 'Sign out', href: '#' },
]

// Set the default active tab to "Overview"
const currentTab = ref(navigation[0])

function setTab(item) {
  currentTab.value = item
  navigation.forEach(n => (n.current = n.name === item.name))
}



//save videos

const videoModules = import.meta.glob('../assets/videos/*.mp4')

const videos = ref([])

onMounted(async () => {
  const videoList = [];
  for (const path in videoModules) {
    const module = await videoModules[path]();
    const fileName = path.split('/').pop();
    videoList.push({
      id: fileName,
      title: metadata[fileName]?.title || fileName,
      videoAlt: metadata[fileName]?.author || 'Unknown',
      description: metadata[fileName]?.description || '',
      date_published: '17 Mar 2025',
      href: "#",
      videoSrc: module.default, // Use the processed URL from Vite
      poster: 'https://tailwindcss.com/plus-assets/img/ecommerce-images/category-page-02-image-card-01.jpg',
    });
  }
  videos.value = videoList
  console.log(videos.value)
})
  

function saveVideo(videoId) {
  console.log("saveVideo pressed for:", videoId)
  console.log("API URL:", import.meta.env.VITE_API_URL);
  axios.post(`${import.meta.env.VITE_API_URL}/categorisation` //'http://localhost:5000/post_video'
  , {
    video_id: videoId
  })
  .then(response => {
    console.log("Response from backend:", response.data)
  })
  .catch(error => {
    console.error("Error while posting video:", error)
  })
}
</script>
