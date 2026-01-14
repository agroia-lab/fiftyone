# Satellite Map with GPS Points
# Using Google Maps Static API

library(ggmap)
library(ggplot2)
library(dplyr)

# Register Google API key
register_google(key = "AIzaSyAtZgwi1Pg2lKi0w5qutlhTX45ilVsnW-k")

# Load data with GPS coordinates
data_path <- "/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-13/santa_ines_with_gps.csv"
df <- read.csv(data_path, stringsAsFactors = FALSE)

# Create category column
df$category <- ifelse(grepl("overview", df$tags), "High Altitude", "Close-up")

cat("Data loaded:\n")
cat(sprintf("  Total images: %d\n", nrow(df)))
cat(sprintf("  Lat range: %.6f to %.6f\n", min(df$latitude), max(df$latitude)))
cat(sprintf("  Lon range: %.6f to %.6f\n", min(df$longitude), max(df$longitude)))

# Calculate center and create bounding box
center_lat <- mean(df$latitude)
center_lon <- mean(df$longitude)

cat(sprintf("\nCenter: %.6f, %.6f\n", center_lat, center_lon))

# Get satellite map from Google
# Zoom level: higher = more detail (18-20 good for drone survey area)
map <- get_googlemap(
  center = c(lon = center_lon, lat = center_lat),
  zoom = 18,
  maptype = "satellite",
  size = c(640, 640)
)

# Create the plot with satellite background
p_satellite <- ggmap(map) +
  geom_point(
    data = df,
    aes(x = longitude, y = latitude, color = category),
    size = 3,
    alpha = 0.8
  ) +
  scale_color_manual(
    values = c("Close-up" = "#00FF00", "High Altitude" = "#FF0000")
  ) +
  labs(
    title = "Santa Ines Drone Survey - GPS Locations",
    subtitle = "Satellite imagery with image capture positions",
    x = "Longitude",
    y = "Latitude",
    color = "Image Type"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(size = 14, face = "bold", color = "white"),
    plot.subtitle = element_text(size = 10, color = "gray80"),
    axis.text = element_text(color = "white"),
    axis.title = element_text(color = "white"),
    legend.background = element_rect(fill = "gray20", color = NA),
    legend.text = element_text(color = "white"),
    legend.title = element_text(color = "white"),
    panel.grid = element_line(color = "gray40", linewidth = 0.2)
  )

# Save the plot
output_path <- "/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-13/r_satellite_gps_map.png"
ggsave(output_path, p_satellite, width = 10, height = 10, dpi = 150)
cat(sprintf("\nSaved: %s\n", output_path))

# Also create a side-by-side comparison: GPS satellite vs Embedding space
library(gridExtra)

# Embedding plot (right panel)
p_embedding <- ggplot(df, aes(x = umap_x, y = umap_y, color = category)) +
  geom_point(size = 3, alpha = 0.8) +
  scale_color_manual(values = c("Close-up" = "#00FF00", "High Altitude" = "#FF0000")) +
  labs(
    title = "CLIP Embedding Space",
    x = "UMAP Dimension 1",
    y = "UMAP Dimension 2",
    color = "Image Type"
  ) +
  theme_minimal() +
  theme(legend.position = "bottom")

# Combined plot
p_combined <- grid.arrange(
  p_satellite + theme(legend.position = "bottom"),
  p_embedding,
  ncol = 2,
  top = "Santa Ines Drone Images: Physical Location vs Visual Similarity"
)

output_combined <- "/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-13/r_gps_vs_embedding_satellite.png"
ggsave(output_combined, p_combined, width = 16, height = 8, dpi = 150)
cat(sprintf("Saved: %s\n", output_combined))

cat("\n=== Complete ===\n")
