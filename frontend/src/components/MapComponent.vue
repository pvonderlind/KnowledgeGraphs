<script>
  import axios from "axios";
  import { ref } from "vue";
  import { onMounted } from "vue";
  import leaflet from "leaflet";

  export default {
    name: "MapComponent",
    components: {},
    data () {
      return {
        numberOfListings: 0,
        error_text: '',
        error: false,
        markers: [],
      }
    },
    setup() {
      let map;
      onMounted(() => {
        map = leaflet.map('map').setView([48.210033, 16.363449], 13);

        leaflet.tileLayer(`https://api.mapbox.com/styles/v1/mapbox/{style_id}/tiles/{z}/{x}/{y}?access_token=${import.meta.env.VITE_MAPBOX}`, {
          maxZoom: 19,
          zoom: 10,
          attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
          style_id: "streets-v8",
          accessToken: import.meta.env.VITE_MAPBOX,
      }).addTo(map);
      })
      const listings = ref([]);

      const markers = ref([]);
      const addMarker = (listing) => {
        leaflet.marker([listing.LATITUDE, listing.LONGITUDE]).addTo(map);
      }
      return {listings, addMarker}
    },
    mounted() {
      axios.get("http://localhost:8000/api/listings/all", {
            headers: {'Content-Type': 'application/json'}
      }).then(response => {
            this.listings = JSON.parse(response.data);
            this.numberOfListings = this.listings.length;
      });
    }
  }
</script>


<template>
    <div id="willhaben_container">
      <h1> Willhaben Listings </h1>
      <h3 style="color:red" v-if="error">{{ error_text }}</h3>
      <div class="container text-center">
          <div class="row row-cols-5">
              <div v-for="l in listings.slice(0, 5)" :key='l.HEADING' class="card">
                  <div class="card-body" @click="addMarker(l)">
                      <h5 class="card-title">{{ l.PRICE }} EUR</h5>
                      <h6 class="card-subtitle mb-2 text-body-secondary"> {{ l.HEADING }}</h6>
                      <p class="card-text">{{ l.POSTCODE }}</p>
                  </div>
              </div>
          </div>
      </div>
    </div>

    <div id="map"></div>
</template>

<style>
body {
  margin: 0;
}
#map {
  height: 400px;
}
</style>