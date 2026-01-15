# La Capilla Drone Imagery Analysis
# FiftyOne Dataset Analysis using R/ggplot2

library(ggplot2)
library(dplyr)

# =============================================================================
# 1. Load Data
# =============================================================================

data_path <- "/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-14/research/datasets/la_capilla/data/la_capilla_data.csv"
output_dir <- "/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-14/research/datasets/la_capilla/figures"

df <- read.csv(data_path, stringsAsFactors = FALSE)

# Create category column from tags
df$category <- ifelse(grepl("very-close-up", df$tags), "Very Close-up", "Medium Altitude")

cat("Dataset Summary:\n")
cat(sprintf("  Total samples: %d\n", nrow(df)))
cat(sprintf("  Very close-up images: %d\n", sum(df$category == "Very Close-up")))
cat(sprintf("  Medium altitude images: %d\n", sum(df$category == "Medium Altitude")))

# =============================================================================
# 2. CLIP Embedding Space Visualization
# =============================================================================

p1 <- ggplot(df, aes(x = umap_x, y = umap_y, color = category)) +
  geom_point(size = 3, alpha = 0.8) +
  scale_color_manual(values = c("Very Close-up" = "#9B59B6", "Medium Altitude" = "#27AE60")) +
  labs(
    title = "CLIP Embedding Space - La Capilla Drone Imagery",
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
  file.path(output_dir, "embeddings_plot.png"),
  p1, width = 10, height = 8, dpi = 150
)
cat("\nSaved: embeddings_plot.png\n")

# =============================================================================
# 3. Image Size Analysis
# =============================================================================

df$size_mb <- df$size_bytes / (1024 * 1024)

p4 <- ggplot(df, aes(x = category, y = size_mb, fill = category)) +
  geom_boxplot(alpha = 0.7) +
  geom_jitter(width = 0.2, alpha = 0.5, size = 2) +
  scale_fill_manual(values = c("Very Close-up" = "#9B59B6", "Medium Altitude" = "#27AE60")) +
  labs(
    title = "Image File Size by Category - La Capilla",
    x = "",
    y = "File Size (MB)",
    fill = "Image Type"
  ) +
  theme_minimal() +
  theme(legend.position = "none")

ggsave(
  file.path(output_dir, "size_analysis.png"),
  p4, width = 8, height = 6, dpi = 150
)
cat("Saved: size_analysis.png\n")

# =============================================================================
# 4. Statistical Summary
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
    mean_size_mb = mean(size_mb, na.rm = TRUE),
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
# 5. Combined Panel Plot with Labels
# =============================================================================

p_combined <- ggplot(df, aes(x = umap_x, y = umap_y)) +
  geom_point(aes(color = category, size = size_mb), alpha = 0.7) +
  scale_color_manual(values = c("Very Close-up" = "#9B59B6", "Medium Altitude" = "#27AE60")) +
  scale_size_continuous(range = c(2, 5), name = "Size (MB)") +
  labs(
    title = "La Capilla Drone Survey - Semantic Clustering",
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
    xmin = -1.5, xmax = 1, ymin = 1, ymax = 4,
    alpha = 0.1, fill = "#9B59B6", color = "#9B59B6", linetype = "dashed"
  ) +
  annotate(
    "text",
    x = -0.25, y = 4.3,
    label = "Very close-up\ncluster",
    size = 3, color = "#9B59B6"
  )

ggsave(
  file.path(output_dir, "combined_analysis.png"),
  p_combined, width = 12, height = 8, dpi = 150
)
cat("Saved: combined_analysis.png\n")

cat("\n=== Analysis Complete ===\n")
