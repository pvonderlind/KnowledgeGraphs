<template>
    <GMapMap
      :center="center"
      :zoom="12"
      map-type-id="terrain"
      style="width: 100vw; height:30rem"
    >
    </GMapMap>
</template>
  <script >
  export default {
    name: 'Map',
    data() {
      return {
        center: {lat: 48.2050491798, lng: 16.3701485194},
      }
    }
  }
  </script>

  <style>
body {
  margin: 0;
}
</style>
  