<template>
    <h1> Willhaben Listings </h1>
    <h3 style="color:red" v-if="error">{{ error_text }}</h3>
    <li v-for="listing in listings">
        {{ listing }}
    </li>
    <h3> listings: {{ listings }} </h3>
</template>

<script>
import axios from "axios";

export default {
    name: 'Listings',
    data() {
        return {
            listings: [],
            numberOfListings: 0,
            error_text: '',
            error: false
        }
    },
    mounted() {
        const res = axios.get("http://localhost:8000/api/listings/all", {
            headers: {'Content-Type': 'application/json'}
        }).then(response => {this.listings = JSON.parse(response.data)})
    }
    
}
</script>