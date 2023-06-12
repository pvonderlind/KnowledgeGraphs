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
          zoom: 15,
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
      const clickedListings = [];
      const showingSimilar = ref(false);

      const addMarker = (listing) => {
        const l_id = `${listing.LATITUDE},${listing.LONGITUDE}`
        if (!clickedListings.includes(l_id)) {
          var marker = leaflet.marker([listing.LATITUDE, listing.LONGITUDE]).addTo(map);
          markers.push(marker);
          clickedListings.push(l_id);
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
        similarSelected.value = [];
        const cls = clusters.value;
        const assigned_cluster = cls[listing.id];
        var similar_listings = listings.value.filter(l => cls[l.id] == assigned_cluster);
        similar_listings = similar_listings.slice(0, 5);
        similarSelected.value = similar_listings;
        showingSimilar.value = true;
      }
      const resetPage = () => {
        similarSelected.value = [];
        showingSimilar.value=false;
        for(var i = 0; i < markers.length; i++) {
          map.removeLayer(markers[i]);
        }
      }
      return {listings, stops, clusters, markers, clickedListings, showingSimilar, similarSelected, addMarker, addStop, showSimilar, resetPage}
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
      <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <a class="navbar-brand">Willhaben Browser</a>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav">
            <li class="nav-item">
              <button class="btn btn-outline-danger" @click="resetPage">Reset page</button>
            </li>
          </ul>
        </div>
      </nav>

      <h3 style="color:red" v-if="error">{{ error_text }}</h3>
      <div class="container"  v-show="!showingSimilar">
          <div class="row row-cols-5">
              <div v-for="l in listings.slice(0, 5)" :key='l.id' class="card">
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
        <div class="container" v-show="similarSelected.length > 0 && showingSimilar">
          <div class="row justify-content-between align-items-center">
            <div class="col-11">
              <h1>Similar flats:</h1>
            </div>
            <div class="col-1">
              <button class="btn btn-primary" @click="showingSimilar=false">Back</button>
            </div>
          </div>
          <div class="row row-cols-5">
            <div v-for="l in similarSelected" :key="l.id" class="card">
                <h5 class="card-title">{{ l.PRICE }} EUR</h5>
                <h6 id='text-heading' class="card-subtitle mb-2 text-body-secondary"> {{ l.HEADING }}</h6>
                <p class="card-text">{{ l.POSTCODE }}</p>
                <div id="btn-row">
                  <button type="button" class="btn btn-success" @click="addMarker(l)">Add</button>
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
  height:50vw;
}
</style>