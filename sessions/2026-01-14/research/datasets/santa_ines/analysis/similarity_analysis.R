# Similarity Network Analysis
# Visualize image similarity relationships using R

library(ggplot2)
library(dplyr)

# =============================================================================
# Load Data
# =============================================================================

data_path <- "/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-13/santa_ines_data.csv"
neighbors_path <- "/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-13/similarity_neighbors.csv"

df <- read.csv(data_path, stringsAsFactors = FALSE)
neighbors <- read.csv(neighbors_path, stringsAsFactors = FALSE)

df$category <- ifelse(grepl("overview", df$tags), "High Altitude", "Close-up")

# =============================================================================
# 1. Similarity Heatmap (Top Neighbors)
# =============================================================================

# Focus on high-altitude images and their neighbors
high_alt_files <- df$filename[df$category == "High Altitude"]

# Get neighbors of high-altitude images
ha_neighbors <- neighbors %>%
  filter(source %in% high_alt_files, rank <= 5) %>%
  left_join(df %>% select(filename, category), by = c("neighbor" = "filename"))

cat("High-altitude image neighbors:\n")
print(ha_neighbors %>% count(category))

# =============================================================================
# 2. Distance Distribution Plot
# =============================================================================

# Add category info to neighbors
neighbors_with_cat <- neighbors %>%
  left_join(df %>% select(filename, category), by = c("source" = "filename")) %>%
  rename(source_cat = category) %>%
  left_join(df %>% select(filename, category), by = c("neighbor" = "filename")) %>%
  rename(neighbor_cat = category)

# Compare within-category vs between-category distances
neighbors_with_cat$pair_type <- ifelse(
  neighbors_with_cat$source_cat == neighbors_with_cat$neighbor_cat,
  "Same Category",
  "Different Category"
)

# Only look at rank 1 (nearest neighbor)
nn_distances <- neighbors_with_cat %>% filter(rank == 1)

p_dist <- ggplot(nn_distances, aes(x = distance, fill = pair_type)) +
  geom_histogram(bins = 30, alpha = 0.7, position = "identity") +
  scale_fill_manual(values = c("Same Category" = "#2E86AB", "Different Category" = "#E94F37")) +
  labs(
    title = "Nearest Neighbor Distance Distribution",
    subtitle = "Within-category neighbors are much closer than between-category",
    x = "Euclidean Distance in Embedding Space",
    y = "Count",
    fill = ""
  ) +
  theme_minimal() +
  theme(legend.position = "bottom")

ggsave(
  "/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-13/r_distance_distribution.png",
  p_dist, width = 10, height = 6, dpi = 150
)
cat("\nSaved: r_distance_distribution.png\n")

# =============================================================================
# 3. Similarity Network Visualization
# =============================================================================

# Create edge list for top-3 neighbors only
edges <- neighbors %>%
  filter(rank <= 3) %>%
  select(source, neighbor, distance)

# Get node positions from UMAP
nodes <- df %>% select(filename, umap_x, umap_y, category)

# Merge positions for edge endpoints
edges_with_pos <- edges %>%
  left_join(nodes, by = c("source" = "filename")) %>%
  rename(x_start = umap_x, y_start = umap_y, cat_start = category) %>%
  left_join(nodes, by = c("neighbor" = "filename")) %>%
  rename(x_end = umap_x, y_end = umap_y, cat_end = category)

# Color edges by whether they connect same category
edges_with_pos$edge_type <- ifelse(
  edges_with_pos$cat_start == edges_with_pos$cat_end,
  "Within Category",
  "Cross Category"
)

p_network <- ggplot() +
  # Draw edges
  geom_segment(
    data = edges_with_pos,
    aes(x = x_start, y = y_start, xend = x_end, yend = y_end, color = edge_type),
    alpha = 0.3, linewidth = 0.3
  ) +
  # Draw nodes
  geom_point(
    data = nodes,
    aes(x = umap_x, y = umap_y, fill = category),
    shape = 21, size = 4, color = "white", stroke = 0.5
  ) +
  scale_fill_manual(values = c("Close-up" = "#2E86AB", "High Altitude" = "#E94F37")) +
  scale_color_manual(values = c("Within Category" = "gray70", "Cross Category" = "#FFB703")) +
  labs(
    title = "Image Similarity Network",
    subtitle = "Edges connect each image to its 3 nearest neighbors",
    x = "UMAP Dimension 1",
    y = "UMAP Dimension 2",
    fill = "Image Type",
    color = "Edge Type"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    legend.position = "bottom"
  ) +
  guides(
    fill = guide_legend(order = 1),
    color = guide_legend(order = 2)
  )

ggsave(
  "/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-13/r_similarity_network.png",
  p_network, width = 12, height = 10, dpi = 150
)
cat("Saved: r_similarity_network.png\n")

# =============================================================================
# 4. Cluster Cohesion Analysis
# =============================================================================

# Calculate average distance to k-nearest neighbors by category
cohesion <- neighbors %>%
  filter(rank <= 5) %>%
  left_join(df %>% select(filename, category), by = c("source" = "filename")) %>%
  group_by(category) %>%
  summarise(
    mean_dist = mean(distance),
    sd_dist = sd(distance),
    n = n(),
    .groups = "drop"
  )

cat("\n=== Cluster Cohesion (avg distance to 5 nearest neighbors) ===\n")
print(cohesion)

p_cohesion <- ggplot(cohesion, aes(x = category, y = mean_dist, fill = category)) +
  geom_col(alpha = 0.8, width = 0.6) +
  geom_errorbar(
    aes(ymin = mean_dist - sd_dist, ymax = mean_dist + sd_dist),
    width = 0.2
  ) +
  scale_fill_manual(values = c("Close-up" = "#2E86AB", "High Altitude" = "#E94F37")) +
  labs(
    title = "Cluster Cohesion Analysis",
    subtitle = "High-altitude cluster is tighter (lower avg neighbor distance)",
    x = "",
    y = "Mean Distance to 5 Nearest Neighbors",
    fill = ""
  ) +
  theme_minimal() +
  theme(legend.position = "none")

ggsave(
  "/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-13/r_cluster_cohesion.png",
  p_cohesion, width = 8, height = 6, dpi = 150
)
cat("Saved: r_cluster_cohesion.png\n")

# =============================================================================
# Summary Statistics
# =============================================================================

cat("\n=== Final Summary ===\n")
cat(sprintf("Total images: %d\n", nrow(df)))
cat(sprintf("Close-up images: %d (%.1f%%)\n",
    sum(df$category == "Close-up"),
    100 * sum(df$category == "Close-up") / nrow(df)))
cat(sprintf("High-altitude images: %d (%.1f%%)\n",
    sum(df$category == "High Altitude"),
    100 * sum(df$category == "High Altitude") / nrow(df)))

cross_edges <- sum(edges_with_pos$edge_type == "Cross Category")
total_edges <- nrow(edges_with_pos)
cat(sprintf("Cross-category edges: %d / %d (%.1f%%)\n",
    cross_edges, total_edges, 100 * cross_edges / total_edges))

cat("\n=== Analysis Complete ===\n")
