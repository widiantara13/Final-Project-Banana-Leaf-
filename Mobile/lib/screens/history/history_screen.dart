import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../../constants/api_constants.dart';
import '../../constants/app_colors.dart';
import '../../models/prediction_model.dart';
import '../../providers/predict_provider.dart';
import '../../widgets/prediction_detail_dialog.dart';
import '../profile/edit_profile_screen.dart';

class HistoryScreen extends StatefulWidget {
  final VoidCallback? onBack;

  const HistoryScreen({
    super.key,
    this.onBack,
  });

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  @override
  void initState() {
    super.initState();
    // Ambil riwayat terbaru dari backend saat halaman dibuka
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<PredictProvider>(context, listen: false).fetchHistory();
    });
  }

  /// Format tanggal ramah petani: e.g. "10 Mar 2024, 09:15"
  String _formatDate(DateTime? dateTime) {
    if (dateTime == null) return 'Baru saja';
    try {
      return DateFormat('dd MMM yyyy, HH:mm').format(dateTime.toLocal());
    } catch (_) {
      return 'Baru saja';
    }
  }

  /// Dialog pemilihan filter kondisi daun pisang
  void _showFilterDialog(PredictProvider provider) {
    final filterOptions = [
      'Semua Tanaman',
      'Healthy',
      'Cordana',
      'Sigatoka',
      'Panama',
    ];

    showModalBottomSheet(
      context: context,
      backgroundColor: AppColors.cardSurface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Filter Kondisi Tanaman',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: AppColors.primaryForest,
                ),
              ),
              const SizedBox(height: 14),
              ...filterOptions.map((filter) {
                final isSelected = provider.selectedFilter.toLowerCase() == filter.toLowerCase();
                return ListTile(
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  tileColor: isSelected ? AppColors.primaryLight : null,
                  leading: Icon(
                    isSelected ? Icons.check_circle_rounded : Icons.radio_button_unchecked_rounded,
                    color: isSelected ? AppColors.primary : AppColors.textSecondary,
                  ),
                  title: Text(
                    filter,
                    style: TextStyle(
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
                      color: isSelected ? AppColors.primaryForest : AppColors.textPrimary,
                    ),
                  ),
                  onTap: () {
                    provider.setFilter(filter);
                    Navigator.pop(ctx);
                  },
                );
              }),
            ],
          ),
        ),
      ),
    );
  }

  /// Popup dialog detail hasil prediksi sesuai wireframe
  void _showDetailModal(PredictionResult item) {
    showPredictionDetailDialog(
      context: context,
      prediction: item,
    );
  }

  @override
  Widget build(BuildContext context) {
    final predictProvider = Provider.of<PredictProvider>(context);
    final historyList = predictProvider.filteredHistoryList;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(
            Icons.arrow_back_ios_new_rounded,
            color: AppColors.textPrimary,
            size: 20,
          ),
          onPressed: () {
            if (widget.onBack != null) {
              widget.onBack!();
            } else if (Navigator.canPop(context)) {
              Navigator.pop(context);
            }
          },
        ),
        title: const Text(
          'Riwayat Prediksi',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 20,
            color: AppColors.textPrimary,
          ),
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        actions: [
          IconButton(
            icon: Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: AppColors.primaryLight,
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.settings_outlined,
                color: AppColors.primaryDark,
                size: 22,
              ),
            ),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => const EditProfileScreen(),
                ),
              );
            },
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // ==========================================
            // 1. KONTROL FILTER & URUTKAN (Sesuai Wireframe)
            // ==========================================
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
              child: Row(
                children: [
                  // Tombol 1: Urutkan (Tanggal ↓ / ↑)
                  Expanded(
                    child: GestureDetector(
                      onTap: () => predictProvider.toggleSortDate(),
                      child: Container(
                        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 14),
                        decoration: BoxDecoration(
                          color: AppColors.cardSurface,
                          borderRadius: BorderRadius.circular(18),
                          border: Border.all(color: AppColors.cardBorder, width: 1.2),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.02),
                              blurRadius: 8,
                              offset: const Offset(0, 2),
                            ),
                          ],
                        ),
                        child: Column(
                          children: [
                            const Text(
                              'Urutkan',
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.bold,
                                color: AppColors.textPrimary,
                              ),
                            ),
                            const SizedBox(height: 2),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Text(
                                  predictProvider.sortDateDesc ? '(Tanggal ↓)' : '(Tanggal ↑)',
                                  style: const TextStyle(
                                    fontSize: 11,
                                    color: AppColors.textSecondary,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(width: 12),

                  // Tombol 2: Filter (Semua Tanaman / Kondisi)
                  Expanded(
                    child: GestureDetector(
                      onTap: () => _showFilterDialog(predictProvider),
                      child: Container(
                        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 14),
                        decoration: BoxDecoration(
                          color: AppColors.cardSurface,
                          borderRadius: BorderRadius.circular(18),
                          border: Border.all(color: AppColors.cardBorder, width: 1.2),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.02),
                              blurRadius: 8,
                              offset: const Offset(0, 2),
                            ),
                          ],
                        ),
                        child: Column(
                          children: [
                            const Text(
                              'Filter',
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.bold,
                                color: AppColors.textPrimary,
                              ),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              '(${predictProvider.selectedFilter})',
                              style: const TextStyle(
                                fontSize: 11,
                                color: AppColors.textSecondary,
                                fontWeight: FontWeight.w500,
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 8),

            // ==========================================
            // 2. DAFTAR KARTU RIWAYAT (Sesuai Wireframe)
            // ==========================================
            Expanded(
              child: RefreshIndicator(
                color: AppColors.primary,
                onRefresh: () => predictProvider.fetchHistory(),
                child: predictProvider.isHistoryLoading
                    ? const Center(
                        child: CircularProgressIndicator(color: AppColors.primary),
                      )
                    : historyList.isEmpty
                        ? Center(
                            child: SingleChildScrollView(
                              physics: const AlwaysScrollableScrollPhysics(),
                              padding: const EdgeInsets.all(32),
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Container(
                                    padding: const EdgeInsets.all(20),
                                    decoration: BoxDecoration(
                                      color: AppColors.primaryLight,
                                      shape: BoxShape.circle,
                                    ),
                                    child: const Icon(
                                      Icons.history_rounded,
                                      size: 48,
                                      color: AppColors.primary,
                                    ),
                                  ),
                                  const SizedBox(height: 18),
                                  const Text(
                                    'Belum Ada Riwayat',
                                    style: TextStyle(
                                      fontSize: 18,
                                      fontWeight: FontWeight.bold,
                                      color: AppColors.primaryForest,
                                    ),
                                  ),
                                  const SizedBox(height: 6),
                                  const Text(
                                    'Lakukan prediksi daun pisang pertama Anda di tab Prediksi.',
                                    textAlign: TextAlign.center,
                                    style: TextStyle(
                                      fontSize: 13,
                                      color: AppColors.textSecondary,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          )
                        : ListView.builder(
                            physics: const BouncingScrollPhysics(
                              parent: AlwaysScrollableScrollPhysics(),
                            ),
                            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                            itemCount: historyList.length,
                            itemBuilder: (context, index) {
                              final item = historyList[index];
                              return Container(
                                margin: const EdgeInsets.only(bottom: 14),
                                decoration: BoxDecoration(
                                  color: AppColors.cardSurface,
                                  borderRadius: BorderRadius.circular(22), // Sudut melengkung sesuai wireframe
                                  border: Border.all(
                                    color: AppColors.cardBorder,
                                    width: 1.2,
                                  ),
                                  boxShadow: [
                                    BoxShadow(
                                      color: Colors.black.withOpacity(0.03),
                                      blurRadius: 14,
                                      offset: const Offset(0, 4),
                                    ),
                                  ],
                                ),
                                child: InkWell(
                                  borderRadius: BorderRadius.circular(22),
                                  onTap: () => _showDetailModal(item),
                                  child: Padding(
                                    padding: const EdgeInsets.all(14),
                                    child: Row(
                                      children: [
                                        // 1. Thumbnail Gambar (Sesuai Ikon Wireframe)
                                        Container(
                                          width: 76,
                                          height: 76,
                                          decoration: BoxDecoration(
                                            color: AppColors.inputBackground,
                                            borderRadius: BorderRadius.circular(18),
                                            border: Border.all(
                                              color: AppColors.cardBorder,
                                              width: 1.2,
                                            ),
                                          ),
                                          child: ClipRRect(
                                            borderRadius: BorderRadius.circular(18),
                                            child: (item.imagePath != null && item.imagePath!.isNotEmpty)
                                                ? Image.network(
                                                    ApiConstants.getStaticUrl(item.imagePath!),
                                                    fit: BoxFit.cover,
                                                    errorBuilder: (_, __, ___) => const Center(
                                                      child: Icon(
                                                        Icons.image_outlined,
                                                        size: 40,
                                                        color: AppColors.primary,
                                                      ),
                                                    ),
                                                  )
                                                : const Center(
                                                    child: Icon(
                                                      Icons.image_outlined,
                                                      size: 40,
                                                      color: AppColors.primary,
                                                    ),
                                                  ),
                                          ),
                                        ),

                                        const SizedBox(width: 16),

                                        // 2. Info Kondisi & Tanggal
                                        Expanded(
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              // Nama Penyakit / Kondisi
                                              Text(
                                                item.condition,
                                                style: const TextStyle(
                                                  fontSize: 16,
                                                  fontWeight: FontWeight.bold,
                                                  color: AppColors.primaryForest,
                                                ),
                                              ),
                                              const SizedBox(height: 2),

                                              // Persentase Keyakinan (Akurasi %)
                                              Text(
                                                '(${item.confidence.toStringAsFixed(0)}%)',
                                                style: const TextStyle(
                                                  fontSize: 13,
                                                  fontWeight: FontWeight.bold,
                                                  color: AppColors.primary,
                                                ),
                                              ),
                                              const SizedBox(height: 6),

                                              // Tanggal & Waktu Sesuai Wireframe
                                              Text(
                                                _formatDate(item.createdAt),
                                                style: const TextStyle(
                                                  fontSize: 12,
                                                  color: AppColors.textSecondary,
                                                  fontWeight: FontWeight.w500,
                                                ),
                                              ),
                                            ],
                                          ),
                                        ),

                                        // 3. Ikon Panah Kanan Sesuai Wireframe
                                        const Icon(
                                          Icons.arrow_forward_rounded,
                                          color: AppColors.textPrimary,
                                          size: 20,
                                        ),
                                        const SizedBox(width: 4),
                                      ],
                                    ),
                                  ),
                                ),
                              );
                            },
                          ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

