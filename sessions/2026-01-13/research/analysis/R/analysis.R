# Santa Ines Drone Imagery Analysis
# FiftyOne Dataset Analysis using R/ggplot2

library(ggplot2)
library(dplyr)

# =============================================================================
# 1. Load Data
# =============================================================================

data_path <- "/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-13/santa_ines_data.csv"
df <- read.csv(data_path, stringsAsFactors = FALSE)

# Create category column from tags
df$category <- ifelse(grepl("overview", df$tags), "High Altitude", "Close-up")

cat("Dataset Summary:\n")
cat(sprintf("  Total samples: %d\n", nrow(df)))
cat(sprintf("  Close-up images: %d\n", sum(df$category == "Close-up")))
cat(sprintf("  High altitude images: %d\n", sum(df$category == "High Altitude")))

# =============================================================================
# 2. CLIP Embedding Space Visualization
# =============================================================================

p1 <- ggplot(df, aes(x = umap_x, y = umap_y, color = category)) +
  geom_point(size = 3, alpha = 0.8) +
  scale_color_manual(values = c("Close-up" = "#2E86AB", "High Altitude" = "#E94F37")) +
  labs(
    title = "CLIP Embedding Space - Santa Ines Drone Imagery",
    subtitle = "UMAP 2D projection of ViT-B/32 embeddings",
    x = "UMAP Dimension 1",
    y = "UMAP Dimension 2",
    color = "Image Type"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 10, color = "gray40"),
    legend.position = "bottom"
  )

ggsave(
  "/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-13/r_embeddings_plot.png",
  p1, width = 10, height = 8, dpi = 150
)
cat("\nSaved: r_embeddings_plot.png\n")

# =============================================================================
# 3. Embedding Distribution Analysis
# =============================================================================

p2 <- ggplot(df, aes(x = umap_x, fill = category)) +
  geom_density(alpha = 0.6) +
  scale_fill_manual(values = c("Close-up" = "#2E86AB", "High Altitude" = "#E94F37")) +
  labs(
    title = "UMAP X-Axis Distribution by Category",
    x = "UMAP Dimension 1",
    y = "Density",
    fill = "Image Type"
  ) +
  theme_minimal()

p3 <- ggplot(df, aes(x = umap_y, fill = category)) +
  geom_density(alpha = 0.6) +
  scale_fill_manual(values = c("Close-up" = "#2E86AB", "High Altitude" = "#E94F37")) +
  labs(
    title = "UMAP Y-Axis Distribution by Category",
    x = "UMAP Dimension 2",
    y = "Density",
    fill = "Image Type"
  ) +
  theme_minimal()

# =============================================================================
# 4. Image Size Analysis
# =============================================================================

df$size_mb <- df$size_bytes / (1024 * 1024)

p4 <- ggplot(df, aes(x = category, y = size_mb, fill = category)) +
  geom_boxplot(alpha = 0.7) +
  geom_jitter(width = 0.2, alpha = 0.5, size = 2) +
  scale_fill_manual(values = c("Close-up" = "#2E86AB", "High Altitude" = "#E94F37")) +
  labs(
    title = "Image File Size by Category",
    x = "",
    y = "File Size (MB)",
    fill = "Image Type"
  ) +
  theme_minimal() +
  theme(legend.position = "none")

ggsave(
  "/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-13/r_size_analysis.png",
  p4, width = 8, height = 6, dpi = 150
)
cat("Saved: r_size_analysis.png\n")

# =============================================================================
# 5. Statistical Summary
# =============================================================================

cat("\n=== Statistical Summary ===\n")

summary_stats <- df %>%
  group_by(category) %>%
  summarise(
    n = n(),
    mean_umap_x = mean(umap_x),
    sd_umap_x = sd(umap_x),
    mean_umap_y = mean(umap_y),
    sd_umap_y = sd(umap_y),
    mean_size_mb = mean(size_mb),
    .groups = "drop"
  )

print(summary_stats)

# Centroid distances
cat("\n=== Cluster Centroids ===\n")
centroids <- df %>%
  group_by(category) %>%
  summarise(
    centroid_x = mean(umap_x),
    centroid_y = mean(umap_y),
    .groups = "drop"
  )
print(centroids)

# Calculate inter-cluster distance
dist <- sqrt(
  (centroids$centroid_x[1] - centroids$centroid_x[2])^2 +
  (centroids$centroid_y[1] - centroids$centroid_y[2])^2
)
cat(sprintf("\nInter-cluster distance: %.3f\n", dist))

# =============================================================================
# 6. Combined Panel Plot
# =============================================================================

# Create embedding plot with labeled outliers
df$is_outlier <- df$category == "High Altitude"

p_combined <- ggplot(df, aes(x = umap_x, y = umap_y)) +
  geom_point(aes(color = category, size = size_mb), alpha = 0.7) +
  geom_text(
    data = filter(df, is_outlier),
    aes(label = gsub("DJI_|.JPG", "", filename)),
    vjust = -1, size = 3, color = "gray30"
  ) +
  scale_color_manual(values = c("Close-up" = "#2E86AB", "High Altitude" = "#E94F37")) +
  scale_size_continuous(range = c(2, 5), name = "Size (MB)") +
  labs(
    title = "Santa Ines Drone Survey - Semantic Clustering",
    subtitle = "CLIP embeddings reveal altitude-based image grouping",
    x = "UMAP Dimension 1",
    y = "UMAP Dimension 2",
    color = "Category"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 10, color = "gray40"),
    legend.position = "right"
  ) +
  annotate(
    "rect",
    xmin = 10.5, xmax = 12.5, ymin = -1.5, ymax = 0.5,
    alpha = 0.1, fill = "red", color = "red", linetype = "dashed"
  ) +
  annotate(
    "text",
    x = 11.5, y = 0.8,
    label = "High-altitude\ncluster",
    size = 3, color = "#E94F37"
  )

ggsave(
  "/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-13/r_combined_analysis.png",
  p_combined, width = 12, height = 8, dpi = 150
)
cat("Saved: r_combined_analysis.png\n")

cat("\n=== Analysis Complete ===\n")
