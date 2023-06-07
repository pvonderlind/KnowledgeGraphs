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
        error_text: '',
        error: false,
        showStops: false
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
      const stops = ref([]);
      const listings = ref([]);
      const clusters = ref([]);
      const similarSelected = ref([]);
      const markers = [];

      const addMarker = (listing) => {
        const l_id = `${listing.LATITUDE},${listing.LONGITUDE}`
        if (!markers.includes(l_id)) {
          leaflet.marker([listing.LATITUDE, listing.LONGITUDE]).addTo(map);
          markers.push(l_id);
        }
        map.flyTo([listing.LATITUDE, listing.LONGITUDE], 15);
      }
      const addStop = (stop) => {
        const transicon = leaflet.icon({
          iconUrl: './src/assets/transit.jpg',
          iconSize: [10, 10]
        });
        //leaflet.marker([stop.stop_lat, stop.stop_lon]).addTo(map);
      }
      const showSimilar = (listing) => {
        const cls = clusters.value;
        const assigned_cluster = cls[listing.id];
        const similar_listings = listings.value.filter(l => cls[l.id] == assigned_cluster);
        similarSelected.value.push(similar_listings.slice(0, 5));
      }
      return {listings, stops, clusters, markers, similarSelected, addMarker, addStop, showSimilar}
    },
    mounted() {
      axios.get("http://localhost:8000/api/listings/all", {
            headers: {'Content-Type': 'application/json'}
      }).then(response => {
        this.listings = JSON.parse(response.data);
      });
      axios.get("http://localhost:8000/api/stops/all", {
        headers: {'Content-Type': 'application/json'}
      }).then(response => {
        this.stops = JSON.parse(response.data);
        for (var i = 0; i < this.stops.length; i++) {
          this.addStop(this.stops[i]);
        }
      });
      axios.get("http://localhost:8000/api/clusters/all", {
        headers: {'Content-Type': 'application/json'}
      }).then(response => {
        this.clusters = JSON.parse(response.data);
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
                  <div id='card-listing' class="card-body">
                      <h5 class="card-title">{{ l.PRICE }} EUR</h5>
                      <h6 id='text-heading' class="card-subtitle mb-2 text-body-secondary"> {{ l.HEADING }}</h6>
                      <p class="card-text">{{ l.POSTCODE }}</p>
                        <div id="btn-row">
                          <button type="button" class="btn btn-success" @click="addMarker(l)">Add</button>
                          <button id='similar-btn' type="button" class="btn btn-primary" @click="showSimilar(l)" data-toggle="modal" data-target="#myModal">Show similar</button>
                        </div>
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
#card-listing {
  display: flex;
  justify-content: flex-end;
  flex-direction: column;
}
#btn-row {
  display: flex;
  flex-direction: row;
}
#map {
  height:80vw;
}
</style>