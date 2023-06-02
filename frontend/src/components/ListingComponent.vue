<template>
    <div>
        <h1> Willhaben Listings </h1>
        <h3 style="color:red" v-if="error">{{ error_text }}</h3>
        <div class="container text-center">
            <div class="row row-cols-5">
                <div v-for="l in listings" :key='l.HEADING' class="card">
                    <div class="card-body" @click="add_marker(l)">
                        <h5 class="card-title">{{ l.PRICE }} EUR</h5>
                        <h6 class="card-subtitle mb-2 text-body-secondary"> {{ l.HEADING }}</h6>
                        <p class="card-text">{{ l.POSTCODE }}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
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
        }).then(response => {
            this.listings = JSON.parse(response.data);
            this.numberOfListings = this.listings.length;
        })
    },
    methods: {
        add_marker(listing) {
            //
        }
    }
}
</script>