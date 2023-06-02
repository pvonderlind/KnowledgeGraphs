<script>
import MapComponent from './components/MapComponent.vue';
import ListingComponent from './components/ListingComponent.vue';

export default {
  name: 'App',
  components: {
    MapComponent,
    ListingComponent
  }
}
</script>

<template>
  <div id="app">
    <ListingComponent/>
    <MapComponent/>
  </div>
</template>

<style>
#app {
  display: flex;
  flex-direction: column;
}
</style>
