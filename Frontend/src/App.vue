<script setup>
import HelloWorld from './components/HelloWorld.vue'
import TheWelcome from './components/TheWelcome.vue'
import dashboard from './components/dashboard.vue'
import { useStore } from 'vuex';
import { computed } from 'vue';

const store = useStore();

const email = computed(() => store.getters.user.data?.email)

</script>

<template>

    <!--<dashboard />-->
    <router-view  :email="email"/>

</template>

<style scoped>
header {
  line-height: 1.5;
}


</style>
