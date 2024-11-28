document.addEventListener("DOMContentLoaded", () => {
    const ui = SwaggerUIBundle({
        url: '/openapi.json',  // This is the endpoint that FastAPI generates for the OpenAPI spec
        dom_id: '#swagger-ui',  // The div where Swagger UI will be embedded
        deepLinking: true,
        presets: [
            SwaggerUIBundle.presets.apis,
            SwaggerUIStandalonePreset
        ],
        layout: "BaseLayout",
        onComplete: function() {
            console.log("Swagger UI Loaded");
        }
    });
});