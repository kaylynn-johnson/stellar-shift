'use client';

import { useCallback, useEffect, useState } from 'react';

import { DoubleRangeSlider } from '@/components/DoubleRangeSlider';
import { roundDecimals } from '@/components/format';
import Link from 'next/link';


type Planet = {
  pl_name: string;
  hostname: string;
  pl_rade: number | null;
  pl_orbper: number | null;
  in_hz: number | null;
};

const RADIUS_MIN = 0;
const RADIUS_MAX = 80; // Earth radii

// Setup for log scale
const ORBIT_MIN_DAYS = 0.1;
const ORBIT_MAX_DAYS = 2000;
const ORBIT_MIN_LOG = Math.log10(ORBIT_MIN_DAYS);
const ORBIT_MAX_LOG = Math.log10(ORBIT_MAX_DAYS);

export default function Planets() {
  const [radiusRange, setRadiusRange] = useState<[number, number]>([RADIUS_MIN, RADIUS_MAX]);
  const [orbitRange, setOrbitRange] = useState<[number, number]>([ORBIT_MIN_DAYS, ORBIT_MAX_DAYS]);
  const [discoveryMethod, setDiscoverMethod] = useState("");
  const [spectralType, setSpectralType] = useState("");
  const [discoveryMethods, setDiscoveryMethods] = useState<string[]>([]);
  const [spectralTypes, setSpectralTypes] = useState<string[]>([]);
  const [planets, setPlanets] = useState<Planet[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPlanets = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      // Don't send the max/min value if slider is all the way to the right/left
      if (radiusRange[0] > RADIUS_MIN) params.set('radius_min', String(radiusRange[0]));
      if (radiusRange[1] < RADIUS_MAX) params.set('radius_max', String(radiusRange[1]));
      if (orbitRange[0] > ORBIT_MIN_DAYS) params.set('orbit_period_min', String(roundDecimals(orbitRange[0], 4)));
      if (orbitRange[1] < (ORBIT_MAX_DAYS-10)) params.set('orbit_period_max', String(roundDecimals(orbitRange[1],4)));
      if (discoveryMethod) params.set('discovery_method', discoveryMethod);
      if (spectralType) params.set('spectral_type', spectralType);
      const res = await fetch(`${process.env.NEXT_PUBLIC_FASTAPI_URL}/api/planets/search?${params}`);
      if (!res.ok) {
        setPlanets([]);
        setTotal(0);
        setError(res.status === 404 ? 'No planets match those filters.' : `Request failed (${res.status})`);
        return;
      }
      const data = await res.json();
      setPlanets(data.results);
      setTotal(data.total);
    } catch {
      setError('Could not reach the planets API.');
      setPlanets([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [radiusRange, orbitRange, discoveryMethod, spectralType]);

  useEffect(() => {
    // initial fetching of planets
    fetchPlanets();
  }, []);

  useEffect(() => {
    // one time fetching of discovery method and spectral type options
    fetch(`${process.env.NEXT_PUBLIC_FASTAPI_URL}/api/planets/filter-options`)
    .then(response => response.json())
    .then((data) => {
        setDiscoveryMethods(data.discovery_methods);
        setSpectralTypes(data.spectral_types);
    })
  }, []);

  return (
    <div>
        <h1 className='ml-2 text-3xl font-bold'>Search planets by parameters</h1>

        <div>
            <DoubleRangeSlider
                min={RADIUS_MIN}
                max={RADIUS_MAX}
                value={radiusRange}
                onValueChange={setRadiusRange}
                formatLabel={(v) => `${v} R⊕`}
            />
        </div>
      
        <div>
            <DoubleRangeSlider
                min={ORBIT_MIN_LOG}
                max={ORBIT_MAX_LOG}
                value={[Math.log10(orbitRange[0]), Math.log10(orbitRange[1])]}
                step={0.01}
                onValueChange={([lo, hi]) => setOrbitRange([Math.pow(10, lo), Math.pow(10, hi)])}
                formatLabel={(logValue) => {
                    const days = Math.pow(10, logValue);
                    return days >= (ORBIT_MAX_DAYS-10)
                        ? `${Math.round(days).toLocaleString()}+ days`
                        : days < 1
                            ? days <= ORBIT_MIN_DAYS
                                ? `≤${days.toFixed(2)} days`
                                : `${days.toFixed(2)} days`
                            : `${Math.round(days).toLocaleString()} days`
                }}
            />
        </div>
      
        <div>
            <select 
                value={discoveryMethod} 
                onChange={(e) => setDiscoverMethod(e.target.value)}
                className='rounded-md border border-main bg-white px-3 py-1.5 text-sm ml-2 mb-2'
            >
                <option value="">Any discovery method</option>
                {discoveryMethods.map((m) => (
                    <option key={m} value={m}>{m}</option>
                ))}
            </select>

            <select 
                value={spectralType} 
                onChange={(e) => setSpectralType(e.target.value)}
                className='rounded-md border border-main bg-white px-3 py-1.5 text-sm ml-2 mb-2'
            >
                <option value="">Any stellar type</option>
                {spectralTypes.map((t) => (
                    <option key={t} value={t}>{t}</option>
                ))}
            </select>
        </div>
      
        <button onClick={fetchPlanets} className='rounded-md border border-main bg-white px-3 py-1.5 text-sm ml-2 mb-2'>Search</button>

        {loading && <p className='ml-2 text-xl'>Loading…</p>}
        {error && <p className='ml-2 text-xl'>{error}</p>}

        <div className='ml-2 font-bold'>{total > 25 ? `Showing 25 of ${total} Matching Planets` : `Showing ${total} Matching Planets`}</div>
        <table className='ml-2 table-auto'>
            <thead className='border-b'>
                <tr>
                    <th className='p-3'>Name</th>
                    <th className='p-3'>Earth Radius (R⊕)</th>
                    <th className='p-3'>Orbit Period (days)</th>
                    <th className='p-3'>In Habitable Zone?</th>
                </tr>
            </thead>
            <tbody>
                {planets.map((planet) => (
                    <tr className='border-b'>
                        <td key={planet.pl_name} className='p-3'><Link href={`/planets/${encodeURIComponent(planet.pl_name)}`}>{planet.pl_name}</Link> </td>
                        <td className='p-3'>{planet.pl_rade ?? '?'} </td>
                        <td className='p-3'>{planet.pl_orbper ?? '?'}</td>
                        <td className='p-3'>{planet.in_hz ? 'Yes': 'No'}</td>
                    </tr>
                ))}
            </tbody>  
        </table>
    </div>
  );
}
