# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines for those models you wish to give write DB access
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models

# We're adding a Meta option of 'mario' to the defaults so we can set it for these models
# then the MarioRouter can point at the separate database for these specific models
import django.db.models.options as options
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('mario',)

class Colors(models.Model):
    colorid = models.IntegerField(db_column='colorId', primary_key=True, blank=True) # Field name made lowercase.
    # profileid = models.IntegerField(db_column='profileId', blank=True, null=True) # Field name made lowercase.

    profileid = models.ForeignKey('Profiles', db_column='profileId', blank=True, null=True)

    idx = models.IntegerField(blank=True, null=True)
    r = models.FloatField(blank=True, null=True)
    g = models.FloatField(blank=True, null=True)
    b = models.FloatField(blank=True, null=True)
    class Meta:
        mario = True
        managed = False
        db_table = 'colors'


class Features(models.Model):
    # profileid = models.IntegerField(db_column='profileId', primary_key=True, blank=True) # Field name made lowercase.

    profileid = models.ForeignKey('Profiles', db_column='profileId', primary_key=True, blank=True) # Field name made lowercase.

    grad1_energy = models.FloatField(blank=True, null=True)
    grad1_entropy = models.FloatField(blank=True, null=True)
    grad1_correlation = models.FloatField(blank=True, null=True)
    grad1_inversedifferencemoment = models.FloatField(db_column='grad1_inverseDifferenceMoment', blank=True, null=True) # Field name made lowercase.
    grad1_inertia = models.FloatField(blank=True, null=True)
    grad1_clustershade = models.FloatField(db_column='grad1_clusterShade', blank=True, null=True) # Field name made lowercase.
    grad1_clusterprominence = models.FloatField(db_column='grad1_clusterProminence', blank=True, null=True) # Field name made lowercase.
    grad2_energy = models.FloatField(blank=True, null=True)
    grad2_entropy = models.FloatField(blank=True, null=True)
    grad2_correlation = models.FloatField(blank=True, null=True)
    grad2_inversedifferencemoment = models.FloatField(db_column='grad2_inverseDifferenceMoment', blank=True, null=True) # Field name made lowercase.
    grad2_inertia = models.FloatField(blank=True, null=True)
    grad2_clustershade = models.FloatField(db_column='grad2_clusterShade', blank=True, null=True) # Field name made lowercase.
    grad2_clusterprominence = models.FloatField(db_column='grad2_clusterProminence', blank=True, null=True) # Field name made lowercase.
    energy = models.FloatField(blank=True, null=True)
    entropy = models.FloatField(blank=True, null=True)
    correlation = models.FloatField(blank=True, null=True)
    inversedifferencemoment = models.FloatField(db_column='inverseDifferenceMoment', blank=True, null=True) # Field name made lowercase.
    inertia = models.FloatField(blank=True, null=True)
    clustershade = models.FloatField(db_column='clusterShade', blank=True, null=True) # Field name made lowercase.
    clusterprominence = models.FloatField(db_column='clusterProminence', blank=True, null=True) # Field name made lowercase.
    laplace_energy = models.FloatField(blank=True, null=True)
    laplace_entropy = models.FloatField(blank=True, null=True)
    laplace_correlation = models.FloatField(blank=True, null=True)
    laplace_inversedifferencemoment = models.FloatField(db_column='laplace_inverseDifferenceMoment', blank=True, null=True) # Field name made lowercase.
    laplace_inertia = models.FloatField(blank=True, null=True)
    laplace_clustershade = models.FloatField(db_column='laplace_clusterShade', blank=True, null=True) # Field name made lowercase.
    laplace_clusterprominence = models.FloatField(db_column='laplace_clusterProminence', blank=True, null=True) # Field name made lowercase.
    segment_energy = models.FloatField(blank=True, null=True)
    segment_entropy = models.FloatField(blank=True, null=True)
    segment_correlation = models.FloatField(blank=True, null=True)
    segment_inversedifferencemoment = models.FloatField(db_column='segment_inverseDifferenceMoment', blank=True, null=True) # Field name made lowercase.
    segment_inertia = models.FloatField(blank=True, null=True)
    segment_clustershade = models.FloatField(db_column='segment_clusterShade', blank=True, null=True) # Field name made lowercase.
    segment_clusterprominence = models.FloatField(db_column='segment_clusterProminence', blank=True, null=True) # Field name made lowercase.
    segmentdistances_energy = models.FloatField(db_column='segmentDistances_energy', blank=True, null=True) # Field name made lowercase.
    segmentdistances_entropy = models.FloatField(db_column='segmentDistances_entropy', blank=True, null=True) # Field name made lowercase.
    segmentdistances_correlation = models.FloatField(db_column='segmentDistances_correlation', blank=True, null=True) # Field name made lowercase.
    segmentdistances_inversedifferencemoment = models.FloatField(db_column='segmentDistances_inverseDifferenceMoment', blank=True, null=True) # Field name made lowercase.
    segmentdistances_inertia = models.FloatField(db_column='segmentDistances_inertia', blank=True, null=True) # Field name made lowercase.
    segmentdistances_clustershade = models.FloatField(db_column='segmentDistances_clusterShade', blank=True, null=True) # Field name made lowercase.
    segmentdistances_clusterprominence = models.FloatField(db_column='segmentDistances_clusterProminence', blank=True, null=True) # Field name made lowercase.
    threshold_y_q0 = models.FloatField(db_column='threshold_Y_Q0', blank=True, null=True) # Field name made lowercase.
    threshold_u_q0 = models.FloatField(db_column='threshold_U_Q0', blank=True, null=True) # Field name made lowercase.
    threshold_v_q0 = models.FloatField(db_column='threshold_V_Q0', blank=True, null=True) # Field name made lowercase.
    threshold_y_q1 = models.FloatField(db_column='threshold_Y_Q1', blank=True, null=True) # Field name made lowercase.
    threshold_u_q1 = models.FloatField(db_column='threshold_U_Q1', blank=True, null=True) # Field name made lowercase.
    threshold_v_q1 = models.FloatField(db_column='threshold_V_Q1', blank=True, null=True) # Field name made lowercase.
    threshold_y_q2 = models.FloatField(db_column='threshold_Y_Q2', blank=True, null=True) # Field name made lowercase.
    threshold_u_q2 = models.FloatField(db_column='threshold_U_Q2', blank=True, null=True) # Field name made lowercase.
    threshold_v_q2 = models.FloatField(db_column='threshold_V_Q2', blank=True, null=True) # Field name made lowercase.
    threshold_y_q3 = models.FloatField(db_column='threshold_Y_Q3', blank=True, null=True) # Field name made lowercase.
    threshold_u_q3 = models.FloatField(db_column='threshold_U_Q3', blank=True, null=True) # Field name made lowercase.
    threshold_v_q3 = models.FloatField(db_column='threshold_V_Q3', blank=True, null=True) # Field name made lowercase.
    threshold_y_q4 = models.FloatField(db_column='threshold_Y_Q4', blank=True, null=True) # Field name made lowercase.
    threshold_u_q4 = models.FloatField(db_column='threshold_U_Q4', blank=True, null=True) # Field name made lowercase.
    threshold_v_q4 = models.FloatField(db_column='threshold_V_Q4', blank=True, null=True) # Field name made lowercase.
    thresholdotsu_y = models.FloatField(db_column='thresholdOtsu_Y', blank=True, null=True) # Field name made lowercase.
    thresholdotsu_u = models.FloatField(db_column='thresholdOtsu_U', blank=True, null=True) # Field name made lowercase.
    thresholdotsu_v = models.FloatField(db_column='thresholdOtsu_V', blank=True, null=True) # Field name made lowercase.
    median_y = models.FloatField(db_column='median_Y', blank=True, null=True) # Field name made lowercase.
    median_u = models.FloatField(db_column='median_U', blank=True, null=True) # Field name made lowercase.
    median_v = models.FloatField(db_column='median_V', blank=True, null=True) # Field name made lowercase.
    variance_y = models.FloatField(db_column='variance_Y', blank=True, null=True) # Field name made lowercase.
    standarddeviation_y = models.FloatField(db_column='standardDeviation_Y', blank=True, null=True) # Field name made lowercase.
    skewness_y = models.FloatField(db_column='skewness_Y', blank=True, null=True) # Field name made lowercase.
    kurtosis_y = models.FloatField(db_column='kurtosis_Y', blank=True, null=True) # Field name made lowercase.
    erroronaverage_y = models.FloatField(db_column='errorOnAverage_Y', blank=True, null=True) # Field name made lowercase.
    variance_u = models.FloatField(db_column='variance_U', blank=True, null=True) # Field name made lowercase.
    standarddeviation_u = models.FloatField(db_column='standardDeviation_U', blank=True, null=True) # Field name made lowercase.
    skewness_u = models.FloatField(db_column='skewness_U', blank=True, null=True) # Field name made lowercase.
    kurtosis_u = models.FloatField(db_column='kurtosis_U', blank=True, null=True) # Field name made lowercase.
    erroronaverage_u = models.FloatField(db_column='errorOnAverage_U', blank=True, null=True) # Field name made lowercase.
    variance_v = models.FloatField(db_column='variance_V', blank=True, null=True) # Field name made lowercase.
    standarddeviation_v = models.FloatField(db_column='standardDeviation_V', blank=True, null=True) # Field name made lowercase.
    skewness_v = models.FloatField(db_column='skewness_V', blank=True, null=True) # Field name made lowercase.
    kurtosis_v = models.FloatField(db_column='kurtosis_V', blank=True, null=True) # Field name made lowercase.
    erroronaverage_v = models.FloatField(db_column='errorOnAverage_V', blank=True, null=True) # Field name made lowercase.
    variance_segmentsize = models.FloatField(db_column='variance_SegmentSize', blank=True, null=True) # Field name made lowercase.
    standarddeviation_segmentsize = models.FloatField(db_column='standardDeviation_SegmentSize', blank=True, null=True) # Field name made lowercase.
    skewness_segmentsize = models.FloatField(db_column='skewness_SegmentSize', blank=True, null=True) # Field name made lowercase.
    kurtosis_segmentsize = models.FloatField(db_column='kurtosis_SegmentSize', blank=True, null=True) # Field name made lowercase.
    erroronaverage_segmentsize = models.FloatField(db_column='errorOnAverage_SegmentSize', blank=True, null=True) # Field name made lowercase.
    thresholdotsu_segmentsize = models.FloatField(db_column='thresholdOtsu_SegmentSize', blank=True, null=True) # Field name made lowercase.
    median_segmentsize = models.FloatField(db_column='median_SegmentSize', blank=True, null=True) # Field name made lowercase.
    variance_segmentdistances = models.FloatField(db_column='variance_SegmentDistances', blank=True, null=True) # Field name made lowercase.
    standarddeviation_segmentdistances = models.FloatField(db_column='standardDeviation_SegmentDistances', blank=True, null=True) # Field name made lowercase.
    skewness_segmentdistances = models.FloatField(db_column='skewness_SegmentDistances', blank=True, null=True) # Field name made lowercase.
    kurtosis_segmentdistances = models.FloatField(db_column='kurtosis_SegmentDistances', blank=True, null=True) # Field name made lowercase.
    erroronaverage_segmentdistances = models.FloatField(db_column='errorOnAverage_SegmentDistances', blank=True, null=True) # Field name made lowercase.
    thresholdotsu_segmentdistances = models.FloatField(db_column='thresholdOtsu_SegmentDistances', blank=True, null=True) # Field name made lowercase.
    median_segmentdistances = models.FloatField(db_column='median_SegmentDistances', blank=True, null=True) # Field name made lowercase.
    originalwidth = models.FloatField(db_column='originalWidth', blank=True, null=True) # Field name made lowercase.
    originalheight = models.FloatField(db_column='originalHeight', blank=True, null=True) # Field name made lowercase.
    proportion = models.FloatField(blank=True, null=True)
    orientation = models.FloatField(blank=True, null=True)
    segmentcount = models.FloatField(db_column='segmentCount', blank=True, null=True) # Field name made lowercase.
    jpegcompressionratio = models.FloatField(db_column='jpegCompressionRatio', blank=True, null=True) # Field name made lowercase.
    pngcompressionratio = models.FloatField(db_column='pngCompressionRatio', blank=True, null=True) # Field name made lowercase.
    variance_grad1 = models.FloatField(blank=True, null=True)
    standarddeviation_grad1 = models.FloatField(db_column='standardDeviation_grad1', blank=True, null=True) # Field name made lowercase.
    skewness_grad1 = models.FloatField(blank=True, null=True)
    kurtosis_grad1 = models.FloatField(blank=True, null=True)
    erroronaverage_grad1 = models.FloatField(db_column='errorOnAverage_grad1', blank=True, null=True) # Field name made lowercase.
    thresholdotsu_grad1 = models.FloatField(db_column='thresholdOtsu_grad1', blank=True, null=True) # Field name made lowercase.
    median_grad1 = models.FloatField(blank=True, null=True)
    variance_grad2 = models.FloatField(blank=True, null=True)
    standarddeviation_grad2 = models.FloatField(db_column='standardDeviation_grad2', blank=True, null=True) # Field name made lowercase.
    skewness_grad2 = models.FloatField(blank=True, null=True)
    kurtosis_grad2 = models.FloatField(blank=True, null=True)
    erroronaverage_grad2 = models.FloatField(db_column='errorOnAverage_grad2', blank=True, null=True) # Field name made lowercase.
    thresholdotsu_grad2 = models.FloatField(db_column='thresholdOtsu_grad2', blank=True, null=True) # Field name made lowercase.
    median_grad2 = models.FloatField(blank=True, null=True)
    variance_hough = models.FloatField(blank=True, null=True)
    standarddeviation_hough = models.FloatField(db_column='standardDeviation_hough', blank=True, null=True) # Field name made lowercase.
    skewness_hough = models.FloatField(blank=True, null=True)
    kurtosis_hough = models.FloatField(blank=True, null=True)
    erroronaverage_hough = models.FloatField(db_column='errorOnAverage_hough', blank=True, null=True) # Field name made lowercase.
    thresholdotsu_hough = models.FloatField(db_column='thresholdOtsu_hough', blank=True, null=True) # Field name made lowercase.
    median_hough = models.FloatField(blank=True, null=True)
    hough_energy = models.FloatField(blank=True, null=True)
    hough_entropy = models.FloatField(blank=True, null=True)
    hough_correlation = models.FloatField(blank=True, null=True)
    hough_inversedifferencemoment = models.FloatField(db_column='hough_inverseDifferenceMoment', blank=True, null=True) # Field name made lowercase.
    hough_inertia = models.FloatField(blank=True, null=True)
    hough_clustershade = models.FloatField(db_column='hough_clusterShade', blank=True, null=True) # Field name made lowercase.
    hough_clusterprominence = models.FloatField(db_column='hough_clusterProminence', blank=True, null=True) # Field name made lowercase.
    class Meta:
        mario = True
        managed = False
        db_table = 'features'

class Normalized(models.Model):
    # profileid = models.IntegerField(db_column='profileId', primary_key=True, blank=True) # Field name made lowercase.

    profileid = models.ForeignKey('Profiles', db_column='profileId', primary_key=True, blank=True) # Field name made lowercase.

    grad1_energy = models.FloatField(blank=True, null=True)
    grad1_entropy = models.FloatField(blank=True, null=True)
    grad1_correlation = models.FloatField(blank=True, null=True)
    grad1_inversedifferencemoment = models.FloatField(db_column='grad1_inverseDifferenceMoment', blank=True, null=True) # Field name made lowercase.
    grad1_inertia = models.FloatField(blank=True, null=True)
    grad1_clustershade = models.FloatField(db_column='grad1_clusterShade', blank=True, null=True) # Field name made lowercase.
    grad1_clusterprominence = models.FloatField(db_column='grad1_clusterProminence', blank=True, null=True) # Field name made lowercase.
    grad2_energy = models.FloatField(blank=True, null=True)
    grad2_entropy = models.FloatField(blank=True, null=True)
    grad2_correlation = models.FloatField(blank=True, null=True)
    grad2_inversedifferencemoment = models.FloatField(db_column='grad2_inverseDifferenceMoment', blank=True, null=True) # Field name made lowercase.
    grad2_inertia = models.FloatField(blank=True, null=True)
    grad2_clustershade = models.FloatField(db_column='grad2_clusterShade', blank=True, null=True) # Field name made lowercase.
    grad2_clusterprominence = models.FloatField(db_column='grad2_clusterProminence', blank=True, null=True) # Field name made lowercase.
    energy = models.FloatField(blank=True, null=True)
    entropy = models.FloatField(blank=True, null=True)
    correlation = models.FloatField(blank=True, null=True)
    inversedifferencemoment = models.FloatField(db_column='inverseDifferenceMoment', blank=True, null=True) # Field name made lowercase.
    inertia = models.FloatField(blank=True, null=True)
    clustershade = models.FloatField(db_column='clusterShade', blank=True, null=True) # Field name made lowercase.
    clusterprominence = models.FloatField(db_column='clusterProminence', blank=True, null=True) # Field name made lowercase.
    laplace_energy = models.FloatField(blank=True, null=True)
    laplace_entropy = models.FloatField(blank=True, null=True)
    laplace_correlation = models.FloatField(blank=True, null=True)
    laplace_inversedifferencemoment = models.FloatField(db_column='laplace_inverseDifferenceMoment', blank=True, null=True) # Field name made lowercase.
    laplace_inertia = models.FloatField(blank=True, null=True)
    laplace_clustershade = models.FloatField(db_column='laplace_clusterShade', blank=True, null=True) # Field name made lowercase.
    laplace_clusterprominence = models.FloatField(db_column='laplace_clusterProminence', blank=True, null=True) # Field name made lowercase.
    segment_energy = models.FloatField(blank=True, null=True)
    segment_entropy = models.FloatField(blank=True, null=True)
    segment_correlation = models.FloatField(blank=True, null=True)
    segment_inversedifferencemoment = models.FloatField(db_column='segment_inverseDifferenceMoment', blank=True, null=True) # Field name made lowercase.
    segment_inertia = models.FloatField(blank=True, null=True)
    segment_clustershade = models.FloatField(db_column='segment_clusterShade', blank=True, null=True) # Field name made lowercase.
    segment_clusterprominence = models.FloatField(db_column='segment_clusterProminence', blank=True, null=True) # Field name made lowercase.
    segmentdistances_energy = models.FloatField(db_column='segmentDistances_energy', blank=True, null=True) # Field name made lowercase.
    segmentdistances_entropy = models.FloatField(db_column='segmentDistances_entropy', blank=True, null=True) # Field name made lowercase.
    segmentdistances_correlation = models.FloatField(db_column='segmentDistances_correlation', blank=True, null=True) # Field name made lowercase.
    segmentdistances_inversedifferencemoment = models.FloatField(db_column='segmentDistances_inverseDifferenceMoment', blank=True, null=True) # Field name made lowercase.
    segmentdistances_inertia = models.FloatField(db_column='segmentDistances_inertia', blank=True, null=True) # Field name made lowercase.
    segmentdistances_clustershade = models.FloatField(db_column='segmentDistances_clusterShade', blank=True, null=True) # Field name made lowercase.
    segmentdistances_clusterprominence = models.FloatField(db_column='segmentDistances_clusterProminence', blank=True, null=True) # Field name made lowercase.
    threshold_y_q0 = models.FloatField(db_column='threshold_Y_Q0', blank=True, null=True) # Field name made lowercase.
    threshold_u_q0 = models.FloatField(db_column='threshold_U_Q0', blank=True, null=True) # Field name made lowercase.
    threshold_v_q0 = models.FloatField(db_column='threshold_V_Q0', blank=True, null=True) # Field name made lowercase.
    threshold_y_q1 = models.FloatField(db_column='threshold_Y_Q1', blank=True, null=True) # Field name made lowercase.
    threshold_u_q1 = models.FloatField(db_column='threshold_U_Q1', blank=True, null=True) # Field name made lowercase.
    threshold_v_q1 = models.FloatField(db_column='threshold_V_Q1', blank=True, null=True) # Field name made lowercase.
    threshold_y_q2 = models.FloatField(db_column='threshold_Y_Q2', blank=True, null=True) # Field name made lowercase.
    threshold_u_q2 = models.FloatField(db_column='threshold_U_Q2', blank=True, null=True) # Field name made lowercase.
    threshold_v_q2 = models.FloatField(db_column='threshold_V_Q2', blank=True, null=True) # Field name made lowercase.
    threshold_y_q3 = models.FloatField(db_column='threshold_Y_Q3', blank=True, null=True) # Field name made lowercase.
    threshold_u_q3 = models.FloatField(db_column='threshold_U_Q3', blank=True, null=True) # Field name made lowercase.
    threshold_v_q3 = models.FloatField(db_column='threshold_V_Q3', blank=True, null=True) # Field name made lowercase.
    threshold_y_q4 = models.FloatField(db_column='threshold_Y_Q4', blank=True, null=True) # Field name made lowercase.
    threshold_u_q4 = models.FloatField(db_column='threshold_U_Q4', blank=True, null=True) # Field name made lowercase.
    threshold_v_q4 = models.FloatField(db_column='threshold_V_Q4', blank=True, null=True) # Field name made lowercase.
    thresholdotsu_y = models.FloatField(db_column='thresholdOtsu_Y', blank=True, null=True) # Field name made lowercase.
    thresholdotsu_u = models.FloatField(db_column='thresholdOtsu_U', blank=True, null=True) # Field name made lowercase.
    thresholdotsu_v = models.FloatField(db_column='thresholdOtsu_V', blank=True, null=True) # Field name made lowercase.
    median_y = models.FloatField(db_column='median_Y', blank=True, null=True) # Field name made lowercase.
    median_u = models.FloatField(db_column='median_U', blank=True, null=True) # Field name made lowercase.
    median_v = models.FloatField(db_column='median_V', blank=True, null=True) # Field name made lowercase.
    variance_y = models.FloatField(db_column='variance_Y', blank=True, null=True) # Field name made lowercase.
    standarddeviation_y = models.FloatField(db_column='standardDeviation_Y', blank=True, null=True) # Field name made lowercase.
    skewness_y = models.FloatField(db_column='skewness_Y', blank=True, null=True) # Field name made lowercase.
    kurtosis_y = models.FloatField(db_column='kurtosis_Y', blank=True, null=True) # Field name made lowercase.
    erroronaverage_y = models.FloatField(db_column='errorOnAverage_Y', blank=True, null=True) # Field name made lowercase.
    variance_u = models.FloatField(db_column='variance_U', blank=True, null=True) # Field name made lowercase.
    standarddeviation_u = models.FloatField(db_column='standardDeviation_U', blank=True, null=True) # Field name made lowercase.
    skewness_u = models.FloatField(db_column='skewness_U', blank=True, null=True) # Field name made lowercase.
    kurtosis_u = models.FloatField(db_column='kurtosis_U', blank=True, null=True) # Field name made lowercase.
    erroronaverage_u = models.FloatField(db_column='errorOnAverage_U', blank=True, null=True) # Field name made lowercase.
    variance_v = models.FloatField(db_column='variance_V', blank=True, null=True) # Field name made lowercase.
    standarddeviation_v = models.FloatField(db_column='standardDeviation_V', blank=True, null=True) # Field name made lowercase.
    skewness_v = models.FloatField(db_column='skewness_V', blank=True, null=True) # Field name made lowercase.
    kurtosis_v = models.FloatField(db_column='kurtosis_V', blank=True, null=True) # Field name made lowercase.
    erroronaverage_v = models.FloatField(db_column='errorOnAverage_V', blank=True, null=True) # Field name made lowercase.
    variance_segmentsize = models.FloatField(db_column='variance_SegmentSize', blank=True, null=True) # Field name made lowercase.
    standarddeviation_segmentsize = models.FloatField(db_column='standardDeviation_SegmentSize', blank=True, null=True) # Field name made lowercase.
    skewness_segmentsize = models.FloatField(db_column='skewness_SegmentSize', blank=True, null=True) # Field name made lowercase.
    kurtosis_segmentsize = models.FloatField(db_column='kurtosis_SegmentSize', blank=True, null=True) # Field name made lowercase.
    erroronaverage_segmentsize = models.FloatField(db_column='errorOnAverage_SegmentSize', blank=True, null=True) # Field name made lowercase.
    thresholdotsu_segmentsize = models.FloatField(db_column='thresholdOtsu_SegmentSize', blank=True, null=True) # Field name made lowercase.
    median_segmentsize = models.FloatField(db_column='median_SegmentSize', blank=True, null=True) # Field name made lowercase.
    variance_segmentdistances = models.FloatField(db_column='variance_SegmentDistances', blank=True, null=True) # Field name made lowercase.
    standarddeviation_segmentdistances = models.FloatField(db_column='standardDeviation_SegmentDistances', blank=True, null=True) # Field name made lowercase.
    skewness_segmentdistances = models.FloatField(db_column='skewness_SegmentDistances', blank=True, null=True) # Field name made lowercase.
    kurtosis_segmentdistances = models.FloatField(db_column='kurtosis_SegmentDistances', blank=True, null=True) # Field name made lowercase.
    erroronaverage_segmentdistances = models.FloatField(db_column='errorOnAverage_SegmentDistances', blank=True, null=True) # Field name made lowercase.
    thresholdotsu_segmentdistances = models.FloatField(db_column='thresholdOtsu_SegmentDistances', blank=True, null=True) # Field name made lowercase.
    median_segmentdistances = models.FloatField(db_column='median_SegmentDistances', blank=True, null=True) # Field name made lowercase.
    originalwidth = models.FloatField(db_column='originalWidth', blank=True, null=True) # Field name made lowercase.
    originalheight = models.FloatField(db_column='originalHeight', blank=True, null=True) # Field name made lowercase.
    proportion = models.FloatField(blank=True, null=True)
    orientation = models.FloatField(blank=True, null=True)
    segmentcount = models.FloatField(db_column='segmentCount', blank=True, null=True) # Field name made lowercase.
    jpegcompressionratio = models.FloatField(db_column='jpegCompressionRatio', blank=True, null=True) # Field name made lowercase.
    pngcompressionratio = models.FloatField(db_column='pngCompressionRatio', blank=True, null=True) # Field name made lowercase.
    variance_grad1 = models.FloatField(blank=True, null=True)
    standarddeviation_grad1 = models.FloatField(db_column='standardDeviation_grad1', blank=True, null=True) # Field name made lowercase.
    skewness_grad1 = models.FloatField(blank=True, null=True)
    kurtosis_grad1 = models.FloatField(blank=True, null=True)
    erroronaverage_grad1 = models.FloatField(db_column='errorOnAverage_grad1', blank=True, null=True) # Field name made lowercase.
    thresholdotsu_grad1 = models.FloatField(db_column='thresholdOtsu_grad1', blank=True, null=True) # Field name made lowercase.
    median_grad1 = models.FloatField(blank=True, null=True)
    variance_grad2 = models.FloatField(blank=True, null=True)
    standarddeviation_grad2 = models.FloatField(db_column='standardDeviation_grad2', blank=True, null=True) # Field name made lowercase.
    skewness_grad2 = models.FloatField(blank=True, null=True)
    kurtosis_grad2 = models.FloatField(blank=True, null=True)
    erroronaverage_grad2 = models.FloatField(db_column='errorOnAverage_grad2', blank=True, null=True) # Field name made lowercase.
    thresholdotsu_grad2 = models.FloatField(db_column='thresholdOtsu_grad2', blank=True, null=True) # Field name made lowercase.
    median_grad2 = models.FloatField(blank=True, null=True)
    variance_hough = models.FloatField(blank=True, null=True)
    standarddeviation_hough = models.FloatField(db_column='standardDeviation_hough', blank=True, null=True) # Field name made lowercase.
    skewness_hough = models.FloatField(blank=True, null=True)
    kurtosis_hough = models.FloatField(blank=True, null=True)
    erroronaverage_hough = models.FloatField(db_column='errorOnAverage_hough', blank=True, null=True) # Field name made lowercase.
    thresholdotsu_hough = models.FloatField(db_column='thresholdOtsu_hough', blank=True, null=True) # Field name made lowercase.
    median_hough = models.FloatField(blank=True, null=True)
    hough_energy = models.FloatField(blank=True, null=True)
    hough_entropy = models.FloatField(blank=True, null=True)
    hough_correlation = models.FloatField(blank=True, null=True)
    hough_inversedifferencemoment = models.FloatField(db_column='hough_inverseDifferenceMoment', blank=True, null=True) # Field name made lowercase.
    hough_inertia = models.FloatField(blank=True, null=True)
    hough_clustershade = models.FloatField(db_column='hough_clusterShade', blank=True, null=True) # Field name made lowercase.
    hough_clusterprominence = models.FloatField(db_column='hough_clusterProminence', blank=True, null=True) # Field name made lowercase.
    class Meta:
        mario = True
        managed = False
        db_table = 'normalized'

class Profiles(models.Model):
    id = models.IntegerField(primary_key=True, blank=True)
    fileid = models.TextField(db_column='fileId', unique=True, blank=True) # Field name made lowercase.
    version = models.IntegerField(blank=True, null=True)
    class Meta:
        mario = True
        managed = False
        db_table = 'profiles'

class Tag2Profile(models.Model):
    id = models.IntegerField(primary_key=True, blank=True)

    # profileid = models.IntegerField(db_column='profileId', blank=True, null=True) # Field name made lowercase.
    profileid = models.ForeignKey('Profiles', db_column='profileId', blank=True) # Field name made lowercase.

    tagid = models.IntegerField(db_column='tagId', blank=True, null=True) # Field name made lowercase.
    # tagid = models.ForeignKey('Tags', db_column='tagId', blank=True) # Field name made lowercase.

    class Meta:
        mario = True
        managed = False
        db_table = 'tag2profile'

class Tags(models.Model):
    tagid = models.IntegerField(db_column='tagId', primary_key=True, blank=True) # Field name made lowercase.

    # tagid = models.ManyToManyField('Profiles', through='Tag2Profile', db_column='tagId') # Field name made lowercase.
    # tagid = models.ForeignKey('Tag2Profile', to_field='tagid', db_column='tagId', primary_key=True) # Field name made lowercase.

    tag = models.TextField(unique=True, blank=True)
    class Meta:
        mario = True
        managed = False
        db_table = 'tags'

