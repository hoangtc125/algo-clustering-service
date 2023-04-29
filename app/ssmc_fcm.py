import sys
import math
import traceback
import scipy.optimize
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist
from typing import Optional, List


class SSMC_FCM:
    def __init__(
        self,
        dataset: List,
        fields_len: List,
        fields_weight: Optional[List] = [],
        identity: Optional[List] = [],
        supervised_set: Optional[List] = [],
        n_clusters: Optional[int] = 5,
        fuzzi_M: Optional[int] = 2,
        alpha: Optional[float] = 0.6,
        epsilon: Optional[float] = 0.001,
        n_loop: Optional[int] = 50,
        is_plot: Optional[bool] = False,
    ) -> None:
        self.dataset = dataset
        self.fields_len = fields_len
        self.fields_weight = fields_weight if fields_weight else [1] * len(fields_len)
        self.n_clusters = max([n_clusters, len(supervised_set)])
        self.identity = identity if identity else [i for i in range(len(dataset))]
        self.supervised_set = [
            [self.identity.index(j) for j in i] for i in supervised_set
        ]
        self.fuzzi_M = fuzzi_M
        self.alpha = alpha
        self.epsilon = epsilon
        self.membership = [[0] * self.n_clusters for i in range(len(dataset))]
        self.fuzzi_set = [[fuzzi_M] * self.n_clusters for i in range(len(dataset))]
        self.centroid = []
        self.n_loop = n_loop
        self.is_stop = False
        self.pred_labels = [[] for _ in range(self.n_clusters)]
        self.is_plot = is_plot
        self.loss_values = []

    def clustering(self):
        self.__generate_centroid()
        self.__calculate_mean_distance()
        th_loop = 1
        while th_loop <= self.n_loop and not self.is_stop:
            self.is_stop = True
            self.__update_membership(th_loop)
            self.__update_centroid(th_loop)
            self.__calculate_mean_distance()
            self.__calculate_loss_function()
            th_loop += 1
        for idx, membership in enumerate(self.membership):
            id_cluster = np.argmax(membership)
            self.pred_labels[id_cluster].append(self.identity[idx])
        self.pred_labels = np.array(self.pred_labels, dtype=object)
        # for idx, member in enumerate(self.membership):
        #   print(idx, member, np.argmax(member))

    def __calculate_mean_distance(self):
        data = np.array([*self.dataset, *self.centroid])
        __iter = 0
        self.mean_distance = []
        self.min_distance = []
        self.max_distance = []
        for field_len in self.fields_len:
            distance_matrix = pdist(data[:, __iter : __iter + field_len])
            distance_matrix = distance_matrix[distance_matrix != 0]
            self.mean_distance.append(np.mean(distance_matrix))
            self.min_distance.append(min(distance_matrix))
            self.max_distance.append(max(distance_matrix))
            __iter += field_len

    def __generate_centroid(self):
        # computing centroid for supervised clusters
        for supervised_in_cluster in self.supervised_set:
            __centroid = []
            if not supervised_in_cluster:
                continue
            supervised_data = [self.dataset[i] for i in supervised_in_cluster]
            __centroid = np.sum(supervised_data, axis=0) / len(supervised_in_cluster)
            self.centroid.append(__centroid)

        # computing random centroid for unsupervised clusters (apply kmean++)
        for k in range(self.n_clusters - len(self.centroid)):
            ## initialize a list to store distances of data
            ## points from nearest centroid
            dist = []
            for i in range(self.dataset.shape[0]):
                point = self.dataset[i, :]
                d = sys.maxsize

                ## compute distance of 'point' from each of the previously
                ## selected centroid and store the minimum distance
                for j in range(len(self.centroid)):
                    temp_dist = self.__calculate_euclid_distance(point, self.centroid[j])
                    d = min(d, temp_dist)
                dist.append(d)

            ## select data point with maximum distance as our next centroid
            dist = np.array(dist)
            next_centroid = self.dataset[np.argmax(dist), :]
            self.centroid.append(next_centroid)

        self.centroid = np.array(self.centroid)
        self.plot("Initial Centroids")

    def __update_membership(self, th_loop):
        # for idx, member in enumerate(self.membership):
        #   print(idx, member, np.argmax(member))

        fuzzi_M_pow = 1 / (self.fuzzi_M - 1)
        Dij = [
            [
                self.__calculate_point_distance(point, centroid)
                for centroid in self.centroid
            ]
            for point in self.dataset
        ]

        # without supervision
        for id_point in range(len(self.dataset)):
            Dij_pow = []
            sum_Dij_pow = 0
            for id_centroid in range(len(self.centroid)):
                Dik_pow = math.pow(Dij[id_point][id_centroid], fuzzi_M_pow)
                Dij_pow.append(Dik_pow)
                sum_Dij_pow += 1 / Dik_pow

            membership = [1 / (Dik_pow * sum_Dij_pow) for Dik_pow in Dij_pow]
            self.membership[id_point] = membership

        # with supervision
        if th_loop == 2:
            self.__calculate_M2()
        for id_cluster, supervised_cluster in enumerate(self.supervised_set):
            for id_point in supervised_cluster:
                fuzzi_M2 = self.fuzzi_set[id_point][id_cluster]
                dmin = min(Dij[id_point])
                dij = [distance_ij / dmin for distance_ij in Dij[id_point]]
                uij = [
                    math.pow(1 / (self.fuzzi_M * pow(dij[k], 2)), fuzzi_M_pow)
                    if k != id_cluster
                    else 0
                    for k in range(self.n_clusters)
                ]
                right_expression = math.pow(
                    1 / (fuzzi_M2 * pow(dij[id_cluster], 2)), 1 / (fuzzi_M2 - 1)
                )
                uik_pow = (fuzzi_M2 - self.fuzzi_M) / (fuzzi_M2 - 1)

                def __func(uik):
                    res = uik / ((uik + sum(uij)) ** uik_pow) - right_expression
                    return res

                try:
                    uik = scipy.optimize.fsolve(__func, 0)
                    uik = uik[0]
                    if not isinstance(uik, float):
                        raise Exception("uik is complex")
                    uij[id_cluster] = uik
                except:
                    traceback.print_exc()
                    continue
                membership = [uik / sum(uij) for uik in uij]
                self.membership[id_point] = membership

    def __update_centroid(self, th_loop):
        th_centroid = []
        for id_centroid, centroid in enumerate(self.centroid):
            uik_pow = [
                math.pow(
                    self.membership[id_point][id_centroid],
                    self.fuzzi_set[id_point][id_centroid],
                )
                for id_point in range(len(self.dataset))
            ]
            new_centroid = np.sum(
                [uik * point for uik, point in zip(uik_pow, self.dataset)], axis=0
            ) / sum(uik_pow)
            th_centroid.append(new_centroid)
        if (
            sum(
                [
                    self.__calculate_euclid_distance(old_centroid, new_centroid)
                    for old_centroid, new_centroid in zip(self.centroid, th_centroid)
                ]
            )
            > self.epsilon
        ):
            self.is_stop = False
        self.centroid = np.array(th_centroid)
        self.plot(f"{th_loop}-th loop")

    def plot(self, title: Optional[str] = None):
        if not self.is_plot:
            return
        color = iter(plt.cm.rainbow(np.linspace(0, 1, self.n_clusters)))
        for idx, cluster in enumerate(self.supervised_set):
            if not cluster:
                continue
            c = next(color)
            supervised_points = np.array(
                [self.dataset[self.identity.index(id)].tolist() for id in cluster]
            )
            plt.scatter(
                supervised_points[:, 0],
                supervised_points[:, 1],
                marker="x",
                color=c,
                label=f"supervised points {idx}",
            )

        color = iter(plt.cm.rainbow(np.linspace(0, 1, self.n_clusters)))
        cluster_members = [[] for _ in range(self.n_clusters)]
        for point, membership in zip(self.dataset, self.membership):
            id_cluster = np.argmax(membership)
            cluster_members[id_cluster].append(point.tolist())
        for cluster_member in cluster_members:
            if not cluster_member:
                continue
            cluster_member = np.array(cluster_member)
            c = next(color)
            plt.scatter(
                cluster_member[:, 0],
                cluster_member[:, 1],
                marker=".",
                color=c,
                label="cluster points",
            )
        plt.scatter(
            self.centroid[:, 0],
            self.centroid[:, 1],
            color="black",
            label="cluster centroids",
        )
        plt.title(title)
        plt.legend(bbox_to_anchor=(1, 1))
        plt.xlim(min(self.dataset[:, 0]), max(self.dataset[:, 0]))
        plt.ylim(min(self.dataset[:, 1]), max(self.dataset[:, 1]))
        plt.show()

    def __calculate_M2(self):
        for id_cluster, supervised_cluster in enumerate(self.supervised_set):
            for id_point in supervised_cluster:
                if self.membership[id_point][id_cluster] >= self.alpha:
                    continue
                right_expression = self.fuzzi_M * math.pow(
                    (
                        (1 - self.alpha)
                        / (1 / self.membership[id_point][id_cluster] - 1)
                    ),
                    self.fuzzi_M - 1,
                )

                def __func(fuzzi_M2):
                    res = (
                        fuzzi_M2 * math.pow(self.alpha, fuzzi_M2 - 1) - right_expression
                    )
                    return res

                try:
                    fuzzi_M2 = scipy.optimize.fsolve(__func, self.fuzzi_M)
                    fuzzi_M2 = fuzzi_M2[0]
                    if not isinstance(fuzzi_M2, float):
                        raise Exception("fuzzi_M2 is complex")
                    fuzzi_M2 = fuzzi_M2 if fuzzi_M2 > self.fuzzi_M else self.fuzzi_M
                    self.fuzzi_set[id_point] = [fuzzi_M2] * self.n_clusters
                    # print(id_point, self.fuzzi_set[id_point][id_cluster])
                except:
                    traceback.print_exc()

    def __calculate_point_distance(self, p1, p2):
        __iter = 0
        distance = 0
        for field_len, field_weight, mean_distance, min_distance, max_distance in zip(
            self.fields_len,
            self.fields_weight,
            self.mean_distance,
            self.min_distance,
            self.max_distance,
        ):
            __distance = self.__calculate_euclid_distance(
                np.array(p1[__iter : __iter + field_len]),
                np.array(p2[__iter : __iter + field_len]),
            )
            distance += field_weight * (__distance - min_distance) / max_distance
            __iter += field_len
        return distance if distance > 0 else self.epsilon

    def __calculate_cosin_distance(self, p1, p2):
        return np.dot(p1, p2) / (np.linalg.norm(p1) * np.linalg.norm(p2))

    def __calculate_euclid_distance(self, p1, p2):
        return np.linalg.norm(p1 - p2)

    def __calculate_loss_function(self):
        self.loss_values.append(
            sum(
                [
                    sum(
                        [
                            math.pow(
                                self.membership[id_point][id_centroid],
                                self.fuzzi_set[id_point][id_centroid],
                            )
                            * self.__calculate_point_distance(point, centroid)
                            for id_centroid, centroid in enumerate(self.centroid)
                        ]
                    )
                    for id_point, point in enumerate(self.dataset)
                ]
            )
        )
        # if len(self.loss_values) >= 2 and self.loss_values[-1] > self.loss_values[-2]:
        #     self.is_stop = True

    def show_cluster_members(self):
        len_supervised = sum(
            [len(supervised_set) for supervised_set in self.supervised_set]
        )
        len_dataset = len(self.dataset)
        print(
            f"Supervised percentage: {round(100 * len_supervised / len_dataset, 2)}% ({len_supervised}:{len_dataset})"
        )
        print("Cluster members: ")
        for cluster in self.pred_labels:
            print(cluster)

    def show_loss_function(self):
        plt.plot(self.loss_values)
        plt.title("Loss function")
        plt.show()
        print("loss functions: ")
        print(self.loss_values)
