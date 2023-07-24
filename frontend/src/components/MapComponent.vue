<script>
  import axios from "axios";
  import { ref } from "vue";
  import { onMounted } from "vue";
  import leaflet from "leaflet";

  export default {
    name: "MapComponent",
    components: {},
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
      let listingsOnMap = [];
      let stopMarkers = [];
      const showingSimilar = ref(false);
      const transicon = leaflet.icon({
            iconUrl: './src/assets/transit.jpg',
            iconSize: [20, 20]
            });

      const addMarker = (listing) => {
        const l_id = `${listing.LATITUDE},${listing.LONGITUDE}`
        if (!listingsOnMap.includes(l_id)) {
          var marker = leaflet.marker([listing.LATITUDE, listing.LONGITUDE]).addTo(map).bindPopup(listing.HEADING);
          markers.push(marker);
          listingsOnMap.push(l_id);
        }
        map.flyTo([listing.LATITUDE, listing.LONGITUDE], 15);
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
        listingsOnMap = [];
        for(var i = 0; i < markers.length; i++) {
          map.removeLayer(markers[i]);
        }
      }
      const toggleStops = () => {
        if(stopMarkers.length == 0) {
          for (var i = 0; i < stops.value.length; i++) {
            const stop = stops.value[i];
            const stopMarker = leaflet.marker([stop.stop_lat, stop.stop_lon], {icon: transicon}).addTo(map).bindPopup(stop.stop_name);
            stopMarkers.push(stopMarker);
          }
        }else{
          for (var j = 0; j < stopMarkers.length; j++) {
            map.removeLayer(stopMarkers[j]);
          }
          stopMarkers = [];
        }
      }
      return {listings, stops, clusters, markers, listingsOnMap, showingSimilar, similarSelected, addMarker, toggleStops, showSimilar, resetPage}
    },
    data () {
      return {
        error_text: '',
        error: false,
        showStops: false
      }
    },
    mounted() {
      axios.get("http://localhost:8000/api/listings/all", {
            headers: {'Content-Type': 'application/json'}
      }).then(response => {
        //this.listings = JSON.parse(response.data);
        this.listings = response.data;
        console.log(typeof this.listings);
      });
      axios.get("http://localhost:8000/api/stops/all", {
        headers: {'Content-Type': 'application/json'}
      }).then(response => {
        this.stops = JSON.parse(response.data);
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
    <!-- NAVBAR --------------------------------------------- -->
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <a class="navbar-brand">Willhaben Browser</a>
      <div
        id="navbarNav"
        class="collapse navbar-collapse"
      >
        <ul class="nav navbar-nav navbar-right">
          <li class="nav-item">
            <button
              class="btn btn-outline-danger"
              @click="resetPage"
            >
              Reset page
            </button>
          </li>
          <li class="nav-item">
            <button
              class="btn btn-outline-primary"
              @click="toggleStops"
            >
              Toggle Public Transport
            </button>
          </li>
        </ul>
      </div>
    </nav>

    <h3
      v-if="error"
      style="color:red"
    >
      {{ error_text }}
    </h3>

    <!-- LISTING CARD CONTAINER --------------------------------------------- -->
    <div
      v-show="!showingSimilar"
      class="container"
    >
      <div class="row row-col-5">
        <div
          v-for="l in listings.slice(0, 5)"
          :key="l.id"
          class="col card-col"
        >
          <div
            class="card listing-card"
          >
            <div
              class="card-body"
            >
              <h5 class="card-title">
                {{ l.PRICE }} EUR
              </h5>
              <h6
                id="text-heading"
                class="card-subtitle mb-2 text-body-secondary"
              >
                {{ l.HEADING }}
              </h6>
              <p class="card-text">
                {{ l.POSTCODE }}
              </p>
              <div id="btn-row">
                <button
                  type="button"
                  class="btn btn-success"
                  @click="addMarker(l)"
                >
                  +
                </button>
                <button
                  id="similar-btn"
                  type="button"
                  class="btn btn-primary"
                  data-toggle="modal"
                  data-target="#myModal"
                  @click="showSimilar(l)"
                >
                  Show similar
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>




    <!-- SIMILAR LISTINGS CARD CONTAINER --------------------------------------------- -->
    <div
      v-show="similarSelected.length > 0 && showingSimilar"
      class="container"
    >
      <div class="row justify-content-between align-items-center">
        <div class="col-11">
          <h1>Similar flats:</h1>
        </div>
        <div class="col-1">
          <button
            class="btn btn-primary"
            @click="showingSimilar=false"
          >
            Back
          </button>
        </div>
      </div>
      <div class="row row-cols-5">
        <div
          v-for="l in similarSelected"
          :key="l.id"
          class="col card-col"
        >
          <div
            class="card"
          >
            <h5 class="card-title">
              {{ l.PRICE }} EUR
            </h5>
            <h6
              id="text-heading"
              class="card-subtitle mb-2 text-body-secondary"
            >
              {{ l.HEADING }}
            </h6>
            <p class="card-text">
              {{ l.POSTCODE }}
            </p>
            <div id="btn-row">
              <button
                type="button"
                class="btn btn-success"
                @click="addMarker(l)"
              >
                +
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div id="map" />
</template>

<style>
body {
  margin: 0;
}
.card {
  padding: 5px;
}

#map {
  height:50vw;
}
.nav-item {
  margin: 0px 10px 0px 10px;
}
.navbar-brand {
  margin: 0px 10px 0px 10px;
}
nav {
  margin-bottom: 20px;
}
.container {
  margin: 20px 0px 20px 0px;
}
.card-title {
  border-bottom: 1px solid #666666;
}
.card-col {
  display: flex;
}
</style>