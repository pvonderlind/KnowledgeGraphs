<script>
import MapComponent from './components/MapComponent.vue';

export default {
  name: 'App',
  components: {
    MapComponent
  }
}
</script>

<template>
  <div id="app">
    <MapComponent />
  </div>
</template>

<style>
 #app {
  display: flex;
  flex-direction: column;
}
</style>
