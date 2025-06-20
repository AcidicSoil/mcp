use axum::{
    routing::post,
    Json, Router,
    response::{sse::{Sse, Event}, IntoResponse},
    http::StatusCode,
};
use std::{net::SocketAddr, sync::Arc};
use tokio::sync::Notify;
use serde::{Deserialize, Serialize};
use codex_core::{
    Codex,
    config::{Config, ConfigOverrides},
    protocol::{Op, InputItem, EventMsg},
};

// Request structure for the /v1/responses endpoint
#[derive(Debug, Deserialize)]
pub struct ResponsesApiRequest {
    pub input: String,
    pub previous_response_id: Option<String>,
    pub instructions: Option<String>,
    pub store: Option<bool>,
}

// Response structure for streaming events
#[derive(Debug, Serialize)]
pub struct StreamResponse {
    pub event: String,
    pub data: serde_json::Value,
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();

    let app = Router::new()
        .route("/v1/responses", post(responses_endpoint))
        .route("/health", post(health_check));

    let addr = SocketAddr::from(([127, 0, 0, 1], 8080));
    println!("Codex HTTP Server listening on {}", addr);
    println!("Endpoints:");
    println!("  POST /v1/responses - OpenAI-compatible responses endpoint");
    println!("  POST /health - Health check");

    let listener = tokio::net::TcpListener::bind(&addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

// Health check endpoint
async fn health_check() -> impl IntoResponse {
    Json(serde_json::json!({
        "status": "healthy",
        "service": "codex-http-server"
    }))
}

// POST /v1/responses handler
async fn responses_endpoint(
    Json(request): Json<ResponsesApiRequest>,
) -> impl IntoResponse {
    // Create default configuration
    let config = match create_default_config().await {
        Ok(cfg) => cfg,
        Err(e) => {
            tracing::error!("Failed to create config: {}", e);
            return StatusCode::INTERNAL_SERVER_ERROR.into_response();
        }
    };

    // Create Codex instance
    let ctrl_c = Arc::new(Notify::new());
    let (codex, _session_id) = match Codex::spawn(config, ctrl_c).await {
        Ok((codex, session_id)) => (codex, session_id),
        Err(e) => {
            tracing::error!("Failed to spawn Codex: {}", e);
            return StatusCode::INTERNAL_SERVER_ERROR.into_response();
        }
    };

    // Submit user input
    let input_items = vec![InputItem::Text { text: request.input }];
    let user_input = Op::UserInput { items: input_items };

    if let Err(e) = codex.submit(user_input).await {
        tracing::error!("Failed to submit user input: {}", e);
        return StatusCode::INTERNAL_SERVER_ERROR.into_response();
    }

    // Create event stream
    let event_stream = async_stream::stream! {
        loop {
            match codex.next_event().await {
                Ok(event) => {
                    let stream_response = StreamResponse {
                        event: "data".to_string(),
                        data: serde_json::to_value(&event).unwrap_or_default(),
                    };

                    let json = serde_json::to_string(&stream_response).unwrap();
                    yield Ok::<_, std::convert::Infallible>(Event::default().data(json));

                    // Break on task completion or error
                    match &event.msg {
                        EventMsg::TaskComplete(_) | EventMsg::Error(_) => break,
                        _ => {}
                    }
                }
                Err(e) => {
                    tracing::error!("Error receiving event: {}", e);
                    let error_response = StreamResponse {
                        event: "error".to_string(),
                        data: serde_json::json!({ "error": e.to_string() }),
                    };
                    let json = serde_json::to_string(&error_response).unwrap();
                    yield Ok::<_, std::convert::Infallible>(Event::default().data(json));
                    break;
                }
            }
        }
    };

    Sse::new(event_stream).into_response()
}

async fn create_default_config() -> Result<Config, Box<dyn std::error::Error>> {
    // Create a basic default configuration that respects user's config files
    // This will load from ~/.codex/config.toml and environment variables
    let overrides = ConfigOverrides {
        cwd: Some(std::env::current_dir()?),
        // Respect environment variables for model and provider
        model: std::env::var("CODEX_MODEL").ok(),
        model_provider: std::env::var("CODEX_PROVIDER").ok(),
        approval_policy: std::env::var("CODEX_APPROVAL_POLICY")
            .ok()
            .and_then(|s| match s.as_str() {
                "never" => Some(codex_core::protocol::AskForApproval::Never),
                "auto-edit" => Some(codex_core::protocol::AskForApproval::AutoEdit),
                "unless-allow-listed" => Some(codex_core::protocol::AskForApproval::UnlessAllowListed),
                "on-failure" => Some(codex_core::protocol::AskForApproval::OnFailure),
                _ => None,
            }),
        ..Default::default()
    };

    // Load config with CLI args (empty) and overrides
    // This will automatically load from ~/.codex/config.toml if it exists
    let mut config = Config::load_with_cli_overrides(vec![], overrides)
        .map_err(|e| Box::new(e) as Box<dyn std::error::Error>)?;

    // Override Ollama base URL if OLLAMA_BASE_URL environment variable is set
    if let Ok(ollama_base_url) = std::env::var("OLLAMA_BASE_URL") {
        if config.model_provider_id == "ollama" {
            // Create a new provider with the overridden base URL
            let mut ollama_provider = config.model_provider.clone();
            ollama_provider.base_url = ollama_base_url.clone();
            config.model_provider = ollama_provider;
            tracing::info!("Overridden Ollama base URL to: {}", ollama_base_url);
        }
    }

    // Debug: print the loaded configuration
    tracing::info!("Loaded configuration:");
    tracing::info!("  Model: {}", config.model);
    tracing::info!("  Provider: {}", config.model_provider_id);
    tracing::info!("  Approval Policy: {:?}", config.approval_policy);
    tracing::info!("  Codex Home: {:?}", config.codex_home);

    Ok(config)
}